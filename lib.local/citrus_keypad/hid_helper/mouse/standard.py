# adafruit_hid but modified

from adafruit_hid.mouse import Mouse as MS

try:
	from typing import Sequence
	import usb_hid
except Exception:
	pass

from ..utils import find_device


class Mouse(MS):
	def __init__(self, devices: Sequence[usb_hid.Device], timeout: int = None) -> None:
		self._mouse_device = find_device(
			devices, usage_page=0x1, usage=0x02
		)

		# Reuse this bytearray to send mouse reports.
		# report[0] buttons pressed (LEFT, MIDDLE, RIGHT)
		# report[1] x movement
		# report[2] y movement
		# report[3] wheel movement
		self.report = bytearray(4)
