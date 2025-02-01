import supervisor
import asyncio

from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from citrus_keypad.prelude import keycode as KC
from citrus_keypad.ticks_utils import ticks_diff

try:
	from lemon_keypad_rp2040 import LemonKeypadRp2040
except ImportError:
	pass

_exit_button = 0
_caps_lock_button = 1
_dash_button = 2
_dot_button = 3
_backspace = 4
_shift_lock_button = 5

_input_gap_ms = 250

# 0 for dot, 1 for dash, the MSB(1) is a placeholder,
_morse_codes = {
	# letters
	0b1_01: KC.A,
	0b1_1000: KC.B,
	0b1_1010: KC.C,
	0b1_100: KC.D,
	0b1_0: KC.E,
	0b1_0010: KC.F,
	0b1_110: KC.G,
	0b1_0000: KC.H,
	0b1_00: KC.I,
	0b1_0111: KC.J,
	0b1_101: KC.K,
	0b1_0100: KC.L,
	0b1_11: KC.M,
	0b1_10: KC.N,
	0b1_111: KC.O,
	0b1_0110: KC.P,
	0b1_1101: KC.Q,
	0b1_010: KC.R,
	0b1_000: KC.S,
	0b1_1: KC.T,
	0b1_001: KC.U,
	0b1_0001: KC.V,
	0b1_011: KC.W,
	0b1_1001: KC.X,
	0b1_1011: KC.Y,
	0b1_1100: KC.Z,

	# numbers
	0b1_11111: KC.N0,
	0b1_01111: KC.N1,
	0b1_00111: KC.N2,
	0b1_00011: KC.N3,
	0b1_00001: KC.N4,
	0b1_00000: KC.N5,
	0b1_10000: KC.N6,
	0b1_11000: KC.N7,
	0b1_11100: KC.N8,
	0b1_11110: KC.N9,

	# special symbols
	0b1_01000: '&',
	0b1_01110: KC.QUOTE,
	0b1_011010: '@',
	0b1_110011: KC.COMMA,
	0b1_10001: KC.EQUALS,
	0b1_100001: KC.MINUS, # hyphen
	0b1_010101: KC.PERIOD,
	0b1_01010: '+',
	0b1_001100: '?',
	0b1_10010: KC.FORWARD_SLASH,

	# out of spec symbols for convenience
	0b1_0000000: KC.SPACE,
	0b1_1111111: KC.ENTER,
}


def _set_capslock_led(pixels, value):
	pixels[_caps_lock_button] = (0x40, 0, 0) if value else (0, 0, 0)


def _set_shiftlock_led(pixels, value):
	pixels[_shift_lock_button] = (0, 0x40, 100) if value else (0, 0, 0)


async def morse_input(dev: LemonKeypadRp2040) -> None:
	pixels = dev.my_pixels
	pixels.fill((0,0,0,))

	event_queue = dev.my_keypad.events
	layout = KeyboardLayoutUS(dev.current_hid_agent.keyboard)

	shift_lock_status = False
	last_input_timestamp = 0
	current_input = 0b1

	last_capslock_status = layout.keyboard.led_on(layout.keyboard.LED_CAPS_LOCK)
	_set_capslock_led(pixels, last_capslock_status)

	layout.keyboard.release_all()

	while True:
		await asyncio.sleep(0)

		# update capslock led
		if layout.keyboard.led_on(layout.keyboard.LED_CAPS_LOCK) != last_capslock_status:
			last_capslock_status = not last_capslock_status
			_set_capslock_led(pixels, last_capslock_status)

		if current_input > 1 and ticks_diff(supervisor.ticks_ms(), last_input_timestamp) > _input_gap_ms:
			# send new key if has valid input
			code = _morse_codes.get(current_input, None)
			if code is None:
				# red alert, no matching code found
				pixels[_dot_button] = (0x40, 0, 0)
				pixels[_dash_button] = (0x40, 0, 0)
				await asyncio.sleep(0.5) # yeah, more delay for more obvious LED notification
			else:
				# green notice, matching code found
				pixels[_dot_button] = (0, 0x40, 0)
				pixels[_dash_button] = (0, 0x40, 0)
				if isinstance(code, str):
					# some special symbols are easier to send with "layout" object
					layout.write(code)
				else:
					# ordinary keyboard symbols
					# shift lock may override the outcome
					if shift_lock_status:
						layout.keyboard.send(KC.SHIFT, code)
					else:
						layout.keyboard.send(code)
			current_input = 0b1 # clear current input
			await asyncio.sleep(0.1)
			pixels[_dot_button] = (0, 0, 0)
			pixels[_dash_button] = (0, 0, 0)

		new_event = event_queue.get()
		if new_event is None or new_event.released:
			continue

		last_input_timestamp = new_event.timestamp

		# process key events
		if new_event.key_number == _exit_button:
			pixels.fill((0,0,0,))
			layout.keyboard.release_all()
			return
		elif new_event.key_number == _caps_lock_button:
			layout.keyboard.send(KC.CAPS_LOCK)
		elif new_event.key_number == _backspace:
			pixels[_backspace] = (0x40, 0x40, 0)
			s = asyncio.sleep(0.1)
			layout.keyboard.send(KC.BACKSPACE)
			await s
			pixels[_backspace] = (0, 0, 0)
		elif new_event.key_number == _shift_lock_button:
			shift_lock_status = not shift_lock_status
			_set_shiftlock_led(pixels, shift_lock_status)
		elif new_event.key_number in {_dash_button, _dot_button,}:
			if new_event.key_number == _dash_button:
				current_input = (current_input << 1) | 0b1
				pixels[_dash_button] = (0x40, 0x40, 0)
				pixels[_dot_button] = (0, 0, 0)
			else:
				current_input <<= 1
				pixels[_dash_button] = (0, 0, 0)
				pixels[_dot_button] = (0x40, 0x40, 0)
