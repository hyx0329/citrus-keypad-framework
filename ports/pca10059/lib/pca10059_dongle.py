import sys

if sys.implementation._machine != 'PCA10059 nRF52840 Dongle with nRF52840':
	print("WARNING: unsupported platform!")

import alarm
from keypad import Keys
import board

from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from citrus_keypad.prelude import CitrusKeypad, TapDance as TD
import citrus_keypad.keycode as KC

from citrus_keypad.async_event_queue import AsyncEventQueue

# This is testing code on PCA10059
# make a child class to apply hardware specific configurations
class Pca10059Dongle(CitrusKeypad):
	def __init__(self):

		# Prepare necessary sane defaults, and let users happy with the defaults
		self.my_keypad = Keys(
				(board.SW1,),
				value_when_pressed=False,
				pull=True,
			)
		self.my_async_event_queue = AsyncEventQueue(self.my_keypad.events)
		action_map = {
			# 0: (TD(KC.A, KC.B, KC.C, tap_term_ms=500),)
			0: (TD(KC.ESCAPE, KC.ENTER, "It always seems impossible until it's done.", tap_term_ms=500),)
		}

		# initialize citrus keyboard framework
		super().__init__(
			self.my_keypad.events.get,
			action_map,
			ble_enabled=True,
			async_event_getter=self.my_async_event_getter)

		# Some customizations
		# before calling run(), everything can be tweaked on demand
		self.ble_agent.device_info = DeviceInfoService(manufacturer="Citrus Club", software_revision="0.1.0-rc2")
		self.ble_agent.advertise_name = "PCA10059 Dongle"
		# switch to ble by default
		self.switch_to_ble()

	async def my_async_event_getter(self):
		# task switch happens in lower level, `asyncio.sleep` is not required
		return await self.my_async_event_queue

	async def handle_key_action(self, pressed, action) -> bool:
		if await super().handle_key_action(pressed, action):
			# handled by original implementation
			# handles standard keycodes and callables
			return True
		if isinstance(action, str) and pressed:
			# maybe send the string to host via HID interface
			# only handle it when pressed, not released
			self.current_hid_agent.release_all()
			layout = KeyboardLayoutUS(self.current_hid_agent.keyboard)
			layout.write(action)
			return True
		return False

	# example sleep implementation, not used though
	def sleep(self):
		self.my_keypad.deinit()
		alarms = (alarm.pin.PinAlarm(pin=board.SW1, value=False, pull=True),)
		alarm.exit_and_deep_sleep_until_alarms(alarms)

	async def periodic_task_example(self):
		i = 0
		while True:
			await asyncio.sleep(1)
			print(i) # TODO: blink LED?
			i+=1

	def run(self):
		# here's the example to add more custom tasks
		asyncio.get_event_loop().create_task(self.periodic_task_example())
		super().run()
