# -*- encoding: utf-8 -*-
import os

import adafruit_logging as logging
from .consumer_control import ConsumerControl

# TODO: make it switchable
if os.getenv('use_nkro_keyboard'):	
	from .keyboard.nkro import NkroKeyboard as Keyboard
else:
	from .keyboard.standard import Keyboard

# TODO: make it switchable
if os.getenv('use_absolute_mouse'):
	from .mouse.absolute import AbsoluteMouse as Mouse
else:
	from .mouse.standard import Mouse


try:
	from typing import Any
except ImportError:
	pass


logger = logging.getLogger("hid_agent")
if os.getenv('debug'):
	logger.setLevel(logging.DEBUG)
else:
	logger.setLevel(logging.WARNING)


# FIXME: it feels twisted
def pass_through_to(attr_name: str, method_name: str):
	def wrapper_creator(func):
		def wrapper(self, *args, **kwargs):
			real_function = getattr(getattr(self, attr_name, None), method_name, None)
			if callable(real_function):
				setattr(self, func.__name__, real_function)
				return real_function(*args, **kwargs)
			logger.debug('Missing "%s.%s" in instance of "%s"', attr_name, method_name, self.__class__)
		return wrapper
	return wrapper_creator


# HID Agent: wrapper for common HID operations
class HidAgent:

	keyboard: Any
	mouse: Any
	consumer_control: Any

	def __init__(self, devices: list = None):
		self.update_devices(devices)

	def update_devices(self, devices: list = None):
		if devices is None:
			self.keyboard = None
			self.mouse = None
			self.consumer_control = None
			return

		try:
			keyboard = Keyboard(devices)
		except ValueError: # device not found
			keyboard = None

		try:
			mouse = Mouse(devices)
		except ValueError: # device not found
			mouse = None

		try:
			consumer_control = ConsumerControl(devices)
		except ValueError: # device not found
			consumer_control = None

		self.keyboard = keyboard
		self.mouse = mouse
		self.consumer_control = consumer_control

	@pass_through_to('keyboard', 'press')
	def keyboard_press(self, *keycodes: int) -> None:
		pass

	@pass_through_to('keyboard', 'release')
	def keyboard_release(self, *keycodes: int) -> None:
		pass

	@pass_through_to('keyboard', 'release_all')
	def keyboard_release_all(self) -> None:
		pass

	@pass_through_to('keyboard', 'send')
	def keyboard_tap(self, *keycodes: int) -> None:
		pass

	@pass_through_to('keyboard', 'led_on')
	def keyboard_led_on(self, led_code: int) -> bool:
		pass

	@property
	def keyboard_led_status(self) -> bytes:
		return getattr(getattr(self, 'keyboard', None), 'led_status', b'\x00')

	def keyboard_codes(self, pressed: bool, *keycodes: int) -> None:
		if pressed:
			self.keyboard_press(*keycodes)
		else:
			self.keyboard_release(*keycodes)

	@pass_through_to('consumer_control', 'press')
	def consumer_control_press(self, *keycodes: int) -> None:
		pass

	@pass_through_to('consumer_control', 'release')
	def consumer_control_release(self) -> None:
		pass

	@pass_through_to('consumer_control', 'send')
	def consumer_control_tap(self, *keycodes: int) -> None:
		pass

	def consumer_control_codes(self, pressed: bool, *keycodes) -> None:
		if pressed:
			self.consumer_control_press(*keycodes)
		else:
			self.consumer_control_release(*keycodes)

	@pass_through_to('mouse', 'press')
	def mouse_press(self, *keycodes: int) -> None:
		pass

	@pass_through_to('mouse', 'release')
	def mouse_release(self, *keycodes: int) -> None:
		pass

	@pass_through_to('mouse', 'click')
	def mouse_tap(self, *keycodes: int) -> None:
		pass

	@pass_through_to('mouse', 'move')
	def mouse_move(self, x: int = 0, y: int = 0, wheel: int = 0) -> None:
		pass

	@pass_through_to('mouse', 'release_all')
	def mouse_release_all(self) -> None:
		pass

	def release_all(self):
		self.keyboard_release_all()
		self.mouse_release_all()
		# Only one consumer control key can be pressed at a time.
		self.consumer_control_release()

	def mouse_codes(self, pressed: bool, *keycodes) -> None:
		if pressed:
			self.mouse_press(*keycodes)
		else:
			self.mouse_release(*keycodes)
