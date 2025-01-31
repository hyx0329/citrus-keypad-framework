import board
import busio
import digitalio
import microcontroller

from adafruit_bus_device import i2c_device
from adafruit_register.i2c_struct import UnaryStruct
from adafruit_register.i2c_struct_array import StructArray

try:
	from typing import Optional
	from busio import I2C
except ImportError:
	pass


# datasheet: https://www.mouser.com/datasheet/2/198/IS31FL3733_DS-1949479.pdf
class IS31FL3733:

	_command_lock = UnaryStruct(0xFE, "<B")
	_page = UnaryStruct(0xFD, "<B")

	# Read only
	_p3_reset = ROUnaryStruct(0x11, "<B")

	# Write only
	_p3_configuration = UnaryStruct(0x00, "<B")
	_p3_current_control = UnaryStruct(0x01, "<B")
	_p3_breath_abm1 = StructArray(0x02, "<B", 4)
	_p3_breath_abm2 = StructArray(0x06, "<B", 4)
	_p3_breath_abm3 = StructArray(0x0A, "<B", 4)
	_p3_time_update = UnaryStruct(0x0E, "<B")

	def __init__(self, 
				i2c_bus: I2C,
				address: int = 0x50,
				enable_pin: Optional[microcontroller.Pin] = None):
		self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)

		# default POR values
		self._current_page = 0
		self._brightness = 0

		# buffer for LED settings
		self._buffer = bytearray(12 * 16 + 1)
		self._buffer[0] = 0
		self._pixels = memoryview(self._buffer)[1:]
		# track pixels breathing state
		self._pixels_breathing_bitflags = 0

		# there's an enable pin
		self._enable_pin = digitalio.DigitalInOut(enable_pin)
		self._enable_pin.direction = digitalio.Direction.OUTPUT
		self._enable_pin.value = 1

		self.reset()
		self.setup()
		# print(self.open_pixels())
		# print(self.short_pixels())

		self._enable_pin.value = 0

	@property
	def page(self):
		return self._current_page

	@page.setter
	def page(self, value):
		if self._current_page == value:
			return
		self._current_page = value
		self._command_lock = 0xC5
		self._page = value

	def reset(self):
		self.page = 3
		# read to reset
		_ = self._p3_reset

	def setup(self):
		# configure Function Registers at PG3 (0x03)
		# basically breathing control
		self.page = 3

		self._p3_breath_abm1[0] = (0b010_0000_0,)
		self._p3_breath_abm1[1] = (0b010_0011_0,)
		self._p3_breath_abm1[2] = (0b00_00_0000,)
		self._p3_breath_abm1[3] = (0b00000000,) # loop time, 0 for endless

		self._p3_breath_abm1[0] = (0b010_0000_0,)
		self._p3_breath_abm1[1] = (0b010_0010_0,)
		self._p3_breath_abm1[2] = (0b00_00_0000,)
		self._p3_breath_abm1[3] = (0b00000000,) # loop time, 0 for endless

		self._p3_breath_abm1[0] = (0b010_0000_0,)
		self._p3_breath_abm1[1] = (0b010_0001_0,)
		self._p3_breath_abm1[2] = (0b00_00_0000,)
		self._p3_breath_abm1[3] = (0b00000000,) # loop time, 0 for endless

		self._p3_configuration = 0b01 # leave soft-shutdown mode
		self._p3_configuration = 0b11 # breath enable, based on the settings before

		self._p3_time_update = 0

		self.brightness = 0x7F

		self.page(0)
		self.write(0, [255] * 0x18)

	@property
	def enabled(self) -> bool:
		return self._enable_pin.value

	@enabled.setter
	def enabled(self, value: bool):
		self._enable_pin.value = value

	@property
	def brightness(self):
		return self._brightness if self.enabled else 0

	@brightness.setter
	def brightness(self, value: int):
		value = value & 0xFF
		if self._brightness == value:
			return
		self.enabled = True
		self._brightness = value
		self.page = 3
		self._p3_current_control = value

	def update(self):
		self.enabled = True
		self.page = 1
		# write directly for simplicity
		self.i2c_device.write(self._buffer)
		self.eager_sleep()

	def clear(self):
		for i in range(192): # 12*16
			self._pixels[i] = 0

	def set_pixel(self, i, r, g, b):
		"""Set the pixel. It takes effect after calling update()"""
		row = i >> 4  # i // 16
		col = i & 15  # i % 16
		offset = row * 48 + col
		self._pixels[offset] = g
		self._pixels[offset + 16] = r
		self._pixels[offset + 32] = b

	def update_pixel(self, i, r, g, b):
		"""Set the pixel and update"""
		row = i >> 4  # i // 16
		col = i & 15  # i % 16
		offset = row * 48 + col
		self._pixels[offset] = g
		self._pixels[offset + 16] = r
		self._pixels[offset + 32] = b
		self.enabled = True
		self.page = 1
		self.write(offset, g)
		self.write(offset + 16, r)
		self.write(offset + 32, b)
		self.eager_sleep()

	def eager_sleep(self):
		if self._pixels_breathing_bitflags > 0:
			return
		if any(self._pixels):
			return
		self.enabled = False

	def set_pixel_breath_mode(self, i, mode=2):
		self.enabled = True
		self.page = 2
		row = i >> 4  # i // 16
		col = i & 15  # i % 16

		# self.i2c_device.write(bytes((row * 48      + col, mode))) # green
		# self.i2c_device.write(bytes((row * 48 + 16 + col, mode))) # red
		self.i2c_device.write(bytes((row * 48 + 32 + col, mode))) # blue

		if mode > 0:
			self._pixels_breathing_bitflags |= 1 << i
		else:
			self._pixels_breathing_bitflags &= ~(1 << i)
			self.eager_sleep()

	def read_open_pixels(self):
		self.page = 0
		buffer = bytearray(0x18)
		# 18h ~ 2Fh LED Open Register
		self.i2c_device.write_then_readinto(bytes((0x18,)), buffer)
		return buffer

	def read_short_pixels(self):
		self.page = 0
		buffer = bytearray(0x18)
		# 30h ~ 47h LED Short Register
		self.i2c_device.write_then_readinto(bytes((0x30,)), buffer)
		return buffer
