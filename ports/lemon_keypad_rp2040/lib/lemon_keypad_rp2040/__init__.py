import sys
if sys.platform != 'RP2040':
	print("WARNING: unsupported platform! Expecting RP2040!")

import board
import asyncio
from busio import I2C
from keypad import Keys

from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_lsm6ds.lsm6ds3trc import LSM6DS3TRC
from neopixel import NeoPixel

from citrus_keypad.prelude import CitrusKeypad, CompositeAction as CA, TapDance as TD, keycode as KC
from citrus_keypad.async_event_queue import AsyncEventQueue

from .playground.gyro_mouse import gyro_mouse
from .playground.level_gauge import level_gauge
from .playground.morse_input import morse_input


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
		# async friendly queue, read more at `AsyncEventQueue`
		self.my_async_event_queue = AsyncEventQueue(self.my_keypad.events)

		# TODO: load IMU's calibration values
		self.my_imu = imu
		self.my_pixels = pixels
		pixels.fill((0,0,0,)) # clear pixels

		action_map = {
			0: (
				TD(CA(tap=KC.C_PLAY_PAUSE, layer=1), CA(layer="codes"), level_gauge,),
				KC.C_SCAN_NEXT_TRACK,
				KC.C_VOLUME_INCREMENT,
				TD(KC.C_MUTE, CA(layer="codes"), gyro_mouse, None, morse_input,),
				KC.C_VOLUME_DECREMENT,
				KC.C_SCAN_PREVIOUS_TRACK,
			),
			1: (
				None,
				KC.C_FAST_FORWARD,
				None,
				None,
				None,
				KC.C_REWIND,
			),
			"codes": (
				"It always seems impossible until it's done.",
				None,
				None,
				None,
				None,
				None,
			),
		}

		super().__init__(
			self.my_keypad.events.get,
			action_map,
			async_event_getter=self.my_async_event_getter)

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
