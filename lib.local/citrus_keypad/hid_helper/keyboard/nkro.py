from micropython import const

from ..utils import find_device

try:
    from typing import Sequence
    import usb_hid
except ImportError:
    pass


class NkroKeyboard:
	"""Send HID keyboard reports. ALL keys are independent."""

	# The descriptor supports 6 LEDs below, which is all LEDs available per standard
	# mask = 1 << (led_usage_id - 1)
	LED_NUM_LOCK = const(0x01)
	LED_CAPS_LOCK = const(0x02)
	LED_SCROLL_LOCK = const(0x04)
	LED_COMPOSE = const(0x08)
	LED_KANA = const(0x10)
	LED_SHIFT = const(0x40)

	def __init__(self, devices: Sequence[usb_hid.Device]) -> None:
		"""Create a NKRO keyboard, which can have any keys pressed without
		interfering others.
		"""
		self._keyboard_device = find_device(devices, usage_page=0x01, usage=0x06)

		# report[0] modifiers
        # report[1:16] regular key presses

		self.report = bytearray(16)
		self.report_modifier = memoryview(self.report)[0:1]
		self.report_keys = memoryview(self.report)[1:]

		# No keyboard LEDs on.
		self._led_status = b"\x00"

	def press(self, *keycodes: int) -> None:
		for keycode in keycodes:
			if 0xE0 <= keycode < 0xE8:
				# modifiers range, set modifier bit
				self.report_modifier[0] |= 1 << (keycode & 0x7)
			else:
				# key, set corresponding bit
				self.report_keys[keycode >> 3] |= 1 << (keycode & 0x7)
		self._keyboard_device.send_report(self.report)

	def release(self, *keycodes: int) -> None:
		for keycode in keycodes:
			if 0xE0 <= keycode < 0xE8:
				# modifiers range, clear modifier bit
				self.report_modifier[0] &= ~(1 << (keycode & 0x7))
			else:
				# key, clear corresponding bit
				self.report_keys[keycode >> 3] &= ~(1 << (keycode & 0x7))
		self._keyboard_device.send_report(self.report)

	def release_all(self) -> None:
		for i in range(16):
			self.report[i] = 0
		self._keyboard_device.send_report(self.report)

	def send(self, *keycodes: int) -> None:
		# for NKRO, individual keys can be managed without conflicts
		self.press(*keycodes)
		self.release(*keycodes)

	@property
	def led_status(self) -> bytes:
		"""Returns the last received report"""
		# get_last_received_report() returns None when nothing was received
		led_report = self._keyboard_device.get_last_received_report()
		if led_report is not None:
			self._led_status = led_report
		return self._led_status

	def led_on(self, led_code: int) -> bool:
		return bool(self.led_status[0] & led_code)
