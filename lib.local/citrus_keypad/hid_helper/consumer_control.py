# adafruit_hid but modified

from adafruit_hid.consumer_control import ConsumerControl as CC

try:
	from typing import Sequence
	import usb_hid
except Exception:
	pass

from .utils import find_device


class ConsumerControl(CC):
	def __init__(self, devices: Sequence[usb_hid.Device], timeout: int = None) -> None:
		self._consumer_device = find_device(
			devices, usage_page=0x0C, usage=0x01
		)

		# Reuse this bytearray to send consumer reports.
		self._report = bytearray(2)
