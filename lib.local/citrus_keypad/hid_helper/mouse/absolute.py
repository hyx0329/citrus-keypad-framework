# This file is rewritten from absolute_mouse
# part of the original code just makes no sense and looks funny

import struct
from ..utils import find_device

try:
    from typing import Sequence
    import usb_hid
except ImportError:
    pass


class AbsoluteMouse:
	"""Send USB HID mouse reports."""

	LEFT_BUTTON = 1
	"""Left mouse button."""
	RIGHT_BUTTON = 2
	"""Right mouse button."""
	MIDDLE_BUTTON = 4
	"""Middle mouse button."""

	def __init__(self, devices: Sequence[usb_hid.Device]):
		"""Create a Mouse object that will send USB mouse HID reports.

		Devices can be a list of devices that includes a keyboard device or a keyboard device
		itself. A device is any object that implements ``send_report()``, ``usage_page`` and
		``usage``.
		"""
		self._mouse_device = find_device(devices, usage_page=0x1, usage=0x02)
		# Reuse this bytearray to send mouse reports.
		# report[0] buttons pressed (LEFT, MIDDLE, RIGHT)
		# report[1] x1 movement
		# report[2] x2 movement
		# report[3] y1 movement
		# report[4] y2 movement
		# report[5] wheel movement
		self.report = bytearray(6)

		# default at screen center
		struct.pack_into("<HH", self.report, 1, 16383, 16383)

	def press(self, buttons):
		"""Press the given mouse buttons.

		:param buttons: a bitwise-or'd combination of ``LEFT_BUTTON``,
			``MIDDLE_BUTTON``, and ``RIGHT_BUTTON``.

		Examples::

			# Press the left button.
			m.press(Mouse.LEFT_BUTTON)

			# Press the left and right buttons simultaneously.
			m.press(Mouse.LEFT_BUTTON | Mouse.RIGHT_BUTTON)
		"""
		self.report[0] |= buttons
		self._send_report()

	def release(self, buttons):
		"""Release the given mouse buttons.

		:param buttons: a bitwise-or'd combination of ``LEFT_BUTTON``,
			``MIDDLE_BUTTON``, and ``RIGHT_BUTTON``.
		"""
		self.report[0] &= ~buttons
		self._send_report()

	def release_all(self):
		"""Release all the mouse buttons."""
		self.report[0] = 0
		self._send_report()

	def click(self, buttons):
		"""Press and release the given mouse buttons.

		:param buttons: a bitwise-or'd combination of ``LEFT_BUTTON``,
			``MIDDLE_BUTTON``, and ``RIGHT_BUTTON``.

		Examples::

			# Click the left button.
			m.click(Mouse.LEFT_BUTTON)

			# Double-click the left button.
			m.click(Mouse.LEFT_BUTTON)
			m.click(Mouse.LEFT_BUTTON)
		"""
		self.press(buttons)
		self.release(buttons)

	def move(self, x=0, y=0, wheel=0):
		"""Move the mouse and turn the wheel as directed.

		:param x: Set pointer on x axis. 32768 = to the most right, 1 = to the most left, 0 = no move
		:param y: Set pointer on y axis. 32768 = to the bottom, 1 = to the top, 0 = no move
		:param wheel: Rotate the wheel this amount. Negative is toward the user, positive
			is away from the user. The scrolling effect depends on the host.

		Examples::

			# Move to top right corner. Do not move up and down. Do not roll the scroll wheel.
			m.move(32768, 0, 0)
			# Same, with keyword arguments.
			m.move(x=32768, y=0, wheel=0)


			# Roll the mouse wheel away from the user.
			m.move(wheel=1)
		"""

		# Coordinates
		if x > 0:
			x = self._limit_coord(x-1)
			struct.pack_into("<H", self.report, 1, x)
		if y > 0:
			y = self._limit_coord(y-1)
			struct.pack_into("<H", self.report, 3, y)

		# if no scroll, send current cordinates only
		if wheel == 0:
			self.report[5] = 0 # ensure scroll cleared
			self._mouse_device.send_report(self.report)
			return

		# Wheel
		while wheel != 0:
			partial_wheel = self._limit(wheel)
			self.report[5] = partial_wheel & 0xFF
			self._mouse_device.send_report(self.report)
			wheel -= partial_wheel

	def _send_report(self):
		"""Send position & button report."""
		self._mouse_device.send_report(self.report)

	@staticmethod
	def _limit(dist):
		return min(127, max(-127, dist))

	@staticmethod
	def _limit_coord(coord):
		return min(32767, max(0, coord))
