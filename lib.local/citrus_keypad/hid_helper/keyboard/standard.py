# adafruit_hid but modified

from micropython import const
from adafruit_hid.keyboard import Keyboard as KB

try:
	from typing import Sequence
	import usb_hid
except Exception:
	pass

from ..utils import find_device


class Keyboard(KB):

	# The built-in descriptor supports 5 LEDs below
	# mask = 1 << (led_usage_id - 1)
	# LED_NUM_LOCK = const(0x01)
	# LED_CAPS_LOCK = const(0x02)
	# LED_SCROLL_LOCK = const(0x04)
	# LED_COMPOSE = const(0x08)
	LED_KANA = const(0x10) # this one is missed by KB

	def __init__(self, devices: Sequence[usb_hid.Device], timeout: int = None) -> None:
		self._keyboard_device = find_device(
			devices, usage_page=0x1, usage=0x06
		)

		# Reuse this bytearray to send keyboard reports.
		self.report = bytearray(8)

		# report[0] modifiers
		# report[1] unused
		# report[2:8] regular key presses

		# View onto byte 0 in report.
		self.report_modifier = memoryview(self.report)[0:1]

		# List of regular keys currently pressed.
		# View onto bytes 2-7 in report.
		self.report_keys = memoryview(self.report)[2:]

		# No keyboard LEDs on.
		self._led_status = b"\x00"

