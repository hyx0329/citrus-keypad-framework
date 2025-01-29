import sys

if sys.implementation._machine != 'PCA10059 nRF52840 Dongle with nRF52840':
	print("WARNING: unsupported platform!")

import alarm
from keypad import Keys
import board

from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from citrus_keypad.prelude import CitrusKeypad, TapDance as TD
import citrus_keypad.keycode as KC

# This is testing code on PCA10059
# make a child class to apply hardware specific configurations
class EbyteDongle(CitrusKeypad):
	def __init__(self):

		# Prepare necessary sane defaults, and let users happy with the defaults
		keypad = Keys(
				(board.SW1,),
				value_when_pressed=False,
				pull=True,
			)
		action_map = {
			# 0: (TD(KC.A, KC.B, KC.C, tap_term_ms=500),)
			0: (TD(KC.ESCAPE, KC.ENTER, "It always seems impossible until it's done.", tap_term_ms=500),)
		}

		# initialize citrus keyboard framework
		super().__init__(
			keypad,
			action_map,
			ble_enabled=True)

		# Some customizations
		# before calling run(), everything can be tweaked on demand
		self.ble_agent.device_info = DeviceInfoService(manufacturer="Citrus Club", software_revision="0.1.0-rc2")
		self.ble_agent.advertise_name = "Ebyte Dongle"
		# switch to ble by default
		self.switch_to_ble()

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

	# example sleep implementation, not used though
	def sleep(self):
		self.keypad.deinit()
		alarms = (alarm.pin.PinAlarm(pin=board.SW1, value=False, pull=True),)
		alarm.exit_and_deep_sleep_until_alarms(alarms)
