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

	def keyboard_led_on(self, led_code: int) -> bool:
		if self.keyboard is None:
			return False
		return self.keyboard.led_on(led_code)

	@property
	def keyboard_led_status(self) -> bytes:
		return getattr(getattr(self, 'keyboard', None), 'led_status', b'\x00')

	def keyboard_codes(self, pressed: bool, *keycodes: int) -> None:
		"""press/release keyboard keys

		Args:
			pressed (bool): if pressed
			*keycodes: press/release these keys all at once
		"""
		if self.keyboard is None:
			return
		if pressed:
			self.keyboard.press(*keycodes)
		else:
			self.keyboard.release(*keycodes)

	def consumer_control_codes(self, pressed: bool, consumer_code: int) -> None:
		"""Only one consumer code can be activated at the same time. The new
		one will overwrite the old one.

		Args:
			pressed (bool): if pressed
			consumer_code (int): consumer key code
		"""
		if self.consumer_control is None:
			return
		if pressed:
			self.consumer_control.press(consumer_code)
		else:
			self.consumer_control.release()

	def mouse_codes(self, pressed: bool, buttons: int) -> None:
		"""Send mouse codes

		Args:
			pressed (bool): if it's pressed
			buttons (int): a bitwise-or'd combination of precompiled mouse button codes
		"""
		if self.mouse is None:
			return
		if pressed:
			self.mouse.press(buttons)
		else:
			self.mouse.release(buttons)

	def mouse_move(self, x: int = 0, y: int = 0, wheel: int = 0):
		if self.mouse is None:
			return
		self.mouse.move(x, y, wheel)

	def release_all(self):
		if self.keyboard is not None:
			self.keyboard.release_all()
		if self.mouse is not None:
			self.mouse.release_all()
		if self.consumer_control is not None:
			self.consumer_control.release()
