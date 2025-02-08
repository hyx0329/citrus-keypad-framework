import os
import asyncio
import usb_hid
import supervisor
import gc

import adafruit_logging as logging

from .tap_engine import TapEngine
from .tap_engine.utils import is_awaitable
from .hid_helper.agent import HidAgent
from .keycode import MouseCode, ConsumerControlCode

from .ticks_utils import ticks_diff

# not all platforms have ble support
try:
	from .ble_helper import BleHelper
except ImportError:
	pass

try:
	from typing import Any, Dict, Union, Sequence, Callable
	from keypad import Event
except ImportError:
	pass


logger = logging.getLogger("CitrusKeypad")
if os.getenv("debug"):
	logger.setLevel(logging.DEBUG)
else:
	logger.setLevel(logging.WARNING)


class CitrusKeypad:
	def __init__(self,
				event_getter: Callable[[], Event],
				action_map: Dict[Any, Sequence],
				*,
				ble_enabled: bool = False,
				default_layer: Any = 0,
				battery_report_interval_second: int = 90,
				ble_advertising_timeout_second: int = 60):
		# misc configurable settings
		# before calling run(), everything can be directly tweaked
		self.event_getter = event_getter
		self.action_map = action_map
		self.ble_enabled = ble_enabled # setting this value to true will initialize the ble subsystem
		self.default_layer = default_layer
		self.battery_report_interval_second = battery_report_interval_second
		self.ble_advertising_timeout_second = ble_advertising_timeout_second
		# end configurable settings

		# USB interface
		self._hid_usb = HidAgent()

		# track active HID agent
		self._current_active_agent = self._hid_usb
		self._prefer_usb_agent = False

		# core: tap engine
		self._tap_engine = None # created at runtime

	async def handle_key_action(self, pressed, action) -> bool:
		"""Handle real key actions passed by TapEngine. This is the callback.

		Returns True if event is handled.

		TapEngine will catch exceptions here so it will never crash the VM under
		normal circumstances.

		User may override this."""
		# all plain integers are treated as keyboard keycode
		# available via adafruit_hid.keycode.Keycode
		logger.debug("Action: %s, Pressed: %s", action, pressed)
		if isinstance(action, int):
			if isinstance(action, MouseCode):
				# wrapped int cannot work with normal int's __ror__, cast to int
				self._current_active_agent.mouse_codes(pressed, int(action))
			elif isinstance(action, ConsumerControlCode):
				self._current_active_agent.consumer_control_codes(pressed, action)
			else:
				self._current_active_agent.keyboard_codes(pressed, action)
			return True
		elif pressed and callable(action):
			# release all before continuing
			self._current_active_agent.release_all()
			try:
				# call parameters: self,
				result = action(self)
				if is_awaitable(result):
					result = await result
				logger.debug("Function call result: %s", result)
			except Exception as e:
				logger.error("Function call raised an exception: %s: %s", e.__class__.__name__, e)
			# it's handled, right?
			return True
		else:
			return False

	async def task_monitor_usb_change(self) -> None:
		usb_connected_last_time = False

		while True:
			if supervisor.runtime.usb_connected and not usb_connected_last_time:
				# usb just connected, update USB HID agent
				usb_connected_last_time = True
				self._hid_usb.update_devices(usb_hid.devices)
				gc.collect()
				self.update_active_endpoint() # notify about usb change

			if not supervisor.runtime.usb_connected and usb_connected_last_time:
				# usb just disconnected, reset USB HID agent
				usb_connected_last_time = False
				self._hid_usb.update_devices() # remove all devices
				gc.collect()
				self.update_active_endpoint() # notify about usb change

			await asyncio.sleep(1) # poll about once per second

	async def task_ble_adv_management(self) -> None:
		bluetooth_connected_last_time = False

		# auto advertise if haven't advertised since last connection lost

		# NOTE: it seems adv will start automatically after a disconnection, with a timeout
		while True:
			if not self.ble_agent.connected:
				if bluetooth_connected_last_time:
					bluetooth_connected_last_time = False
					self.update_active_endpoint()
				if not self.ble_agent.advertising and self._ble_should_auto_adv:
					# start advertising for once, when not connected
					self._ble_should_auto_adv = False # only start once
					logger.debug("Auto-starting annoymous BLE advertising, timeout %d secs", self.ble_advertising_timeout_second)
					self.ble_agent.start_advertising_advanced(
						connectable=True,
						anonymous=True,
						timeout=self.ble_advertising_timeout_second)
			else:
				self._ble_should_auto_adv = True
				if not bluetooth_connected_last_time:
					bluetooth_connected_last_time = True
					self.update_active_endpoint()

			await asyncio.sleep(1)

	async def task_update_battery_level(self) -> None:
		while True:
			self.ble_agent.battery_level = self.battery_level
			await asyncio.sleep(self.battery_report_interval_second)

	def update_active_endpoint(self) -> None:
		logger.debug("Updating current active HID endpoint")
		if not self.ble_enabled:
			# no need to change
			return

		usb_connected = supervisor.runtime.usb_connected
		ble_connected = self.ble_agent.connected

		if usb_connected and (self._prefer_usb_agent or not ble_connected):
			# a new object may be created, must update
			self._current_active_agent = self._hid_usb
		else:
			# fallback to BLE agent
			self._current_active_agent = self._hid_ble

	def switch_to_usb(self) -> None:
		self._prefer_usb_agent = True
		self.update_active_endpoint()

	def switch_to_ble(self) -> None:
		if not self.ble_enabled:
			return
		self._prefer_usb_agent = False
		self.update_active_endpoint()

	def exception_handler(self, loop, context):
		"""Handle exceptions generated by async tasks.

		Users may override this."""
		print("Handling task termination")
		loop.default_exception_handler(loop, context) # the default one pretty prints the exception

	def run(self):
		self._tap_engine = TapEngine(
			self.event_getter,
			action_map=self.action_map,
			new_event_callback=self.handle_key_action,
			default_layer=self.default_layer,
		)

		loop = asyncio.get_event_loop()
		loop.set_exception_handler(self.exception_handler)

		# engine task, basically the key scanner and preprocesser
		task_engine = loop.create_task(self._tap_engine.run())

		# monitor USB changes
		loop.create_task(self.task_monitor_usb_change())

		# bluetooth advertisment management
		if self.ble_enabled:
			loop.create_task(self.task_ble_adv_management())
			loop.create_task(self.task_update_battery_level())

		# run everything, the engine can represent all major functions
		loop.run_until_complete(task_engine) # run_forever doesn't actually run forever, don't rely on that

	def disconnect_ble(self) -> None:
		self._ble_agent.disconnect_all()

	def start_ble_advertising(self) -> None:
		if self._ble_agent is not None:
			# NOTE: no timeout, will always advertising until connected
			self._ble_agent.start_advertising_advanced(connectable=True, anonymous=True)
			self._ble_should_auto_adv = True # user prefers to adv

	def stop_ble_advertising(self) -> None:
		if self._ble_agent is not None:
			self._ble_agent.stop_advertising()
			self._ble_should_auto_adv = False # user prefers not to adv

	@property
	def battery_level(self) -> int:
		"""Battery level percentage.

		To be overridden by user."""
		return 100

	@property
	def ble_agent(self) -> BleHelper:
		return self._ble_agent

	@property
	def ble_enabled(self) -> bool:
		return getattr(self, '_ble_enabled', False)

	@ble_enabled.setter
	def ble_enabled(self, value: bool):
		self._ble_enabled = value
		if value:
			# initialize BLE components here
			self._ble_agent = BleHelper()
			self._hid_ble = HidAgent(self.ble_agent.devices)
			self._ble_should_auto_adv = True

	@property
	def current_hid_agent(self) -> HidAgent:
		return self._current_active_agent
