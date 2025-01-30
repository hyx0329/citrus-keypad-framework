import sys
if sys.platform != 'RP2040':
	print("WARNING: unsupported platform! Expecting RP2040!")

import board
import asyncio
from busio import I2C
from keypad import Keys

from citrus_keypad.prelude import CitrusKeypad, CompositeAction as CA, TapDance as TD, keycode as KC
from neopixel import NeoPixel
from adafruit_lsm6ds.lsm6ds3trc import LSM6DS3TRC

from .playground.gyro_mouse import gyro_mouse
from .playground.level_gauge import level_gauge


BUTTON_PINS = (board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5,)
I2C_SCL = board.GP9
I2C_SDA = board.GP8
PIXEL_PIN = board.GP7

i2c = I2C(I2C_SCL, I2C_SDA)
imu = LSM6DS3TRC(i2c, 0x6a)
pixels = NeoPixel(PIXEL_PIN, 6)


class LemonKeypadRp2040(CitrusKeypad):
	def __init__(self):
		# Prepare necessary sane defaults, and let users happy with them
		self.my_keypad = Keys(
				BUTTON_PINS,
				value_when_pressed=False,
				pull=True,
			)
		self.my_imu = imu
		self.my_pixels = pixels
		action_map = {
			0: [
				TD(KC.C_PLAY_PAUSE, None, level_gauge,),
				CA(KC.C_SCAN_NEXT_TRACK, KC.C_FAST_FORWARD),
				KC.C_VOLUME_INCREMENT,
				TD(KC.C_MUTE, None, gyro_mouse,),
				KC.C_VOLUME_DECREMENT,
				CA(KC.C_SCAN_PREVIOUS_TRACK, KC.C_REWIND),
			],
		}

		super().__init__(
			self.my_keypad.events.get,
			action_map)
