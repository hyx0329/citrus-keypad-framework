import board
import alarm
import asyncio
import digitalio
import analogio
import supervisor
from busio import I2C
from keypad import KeyMatrix

from citrus_keypad.prelude import CitrusKeypad, keycode as KC, CompositeAction as CA, Transparent

from .hardware_support import MATRIX_ROWS, MATRIX_COLS, MATRIX_COL2ROW_ANODES
from .hardware_support import KEY_COORDS, BATVOLT_TO_PERCENT


i2c = I2C(board.SCL, board.SDA)
___ = Transparent()


class MakerdiaryM60(CitrusKeypad):
	def __init__(self):
		# Prepare necessary sane defaults, and let users happy with them
		self.my_keymatrix = KeyMatrix(
				MATRIX_ROWS,
				MATRIX_COLS,
				MATRIX_COL2ROW_ANODES
			)

		action_map = {
			0: (
				KC.ESC,         KC.N1, KC.N2, KC.N3, KC.N4, KC.N5, KC.N6, KC.N7, KC.N8, KC.N9, KC.N0, KC.MINUS, KC.EQUALS, KC.BACKSPACE,
				KC.TAB,         KC.Q,  KC.W,  KC.E,  KC.R,  KC.T,  KC.Y,  KC.U,  KC.I,  KC.O,  KC.P,  KC.LEFT_BRACKET, KC.RIGHT_BRACKET, KC.BACKSLASH,
				KC.CAPS_LOCK,   KC.A,  KC.S,  KC.D,  KC.F,  KC.G,  KC.H,  KC.J,  KC.K,  KC.L,  KC.SEMICOLON, KC.QUOTE, KC.ENTER,
				KC.LEFT_SHIFT,  KC.Z,  KC.X,  KC.C,  KC.V,  KC.B,  KC.N,  KC.M,  KC.COMMA, KC.PERIOD, KC.FORWARD_SLASH, KC.RIGHT_SHIFT,
				KC.LEFT_CONTROL,KC.LEFT_GUI, KC.LEFT_ALT, KC.SPACE, KC.RIGHT_ALT, KC.MENU, CA(layer='fn'), KC.RIGHT_CONTROL,
			),
			'fn': (
				___,            self.switch_to_usb, self.switch_to_ble, ___,             ___,   ___,   ___,   ___,   ___,   ___,   ___,   ___,      ___,       ___,
				___,            ___,                KC.UP_ARROW,        ___,             ___,   ___,   ___,   ___,   ___,   ___,   ___,   ___,      ___,       ___,
				___,            KC.LEFT_ARROW,      KC.DOWN_ARROW,      KC.RIGHT_ARROW,  ___,   ___,   ___,   ___,   ___,   ___,   ___,   ___,                 ___,
				___,            ___,                ___,                ___,             ___,   ___,   ___,   ___,   ___,   ___,   ___,                        ___,
				___,            ___,   ___,                        ___,                        ___,   ___,      ___,       ___,
			),
		}

		super().__init__(
			self.new_event_with_transform,
			action_map,
			ble_enabled=True,
			sleep_timer_second=1800)

		self.switch_to_ble()

		self.my_charging_sense = digitalio.DigitalInOut(board.CHARGING)
		self.my_charging_sense.pull = digitalio.Pull.UP
		self.my_bat_voltage_sense = analogio.AnalogIn(board.BATTERY)

	def new_event_with_transform(self):
		new_event = self.my_keymatrix.events.get()
		if new_event is not None:
			new_event.key_number = KEY_COORDS[new_event.key_number]
		return new_event

	async def handle_key_action(self, pressed, action) -> bool:
		# TODO: switch profile, connection management
		return super().handle_key_action(pressed, action)

	# def run(self):
	# 	loop = asyncio.get_event_loop()
	# 	# TODO: register backlight control
	# 	# TODO: maybe low battery power off?
	# 	del loop
	# 	# run
	# 	super().run()

	# async def task_backlight_management(self):
	# 	while True:
	# 		# TODO: backlight implementation
	# 		await asyncio.sleep(1)

	@property
	def battery_level(self) -> int:
		BATTERY_LIMIT = 3100  # Cutoff voltage [mV].
		BATTERY_FULLLIMIT = 4190  # Full charge definition [mV].
		BATTERY_DELTA = 10  # mV between each element in the SoC vector.
		# ref voltage: 3.3V
		# bridge: 1M + 1M
		# measured = real / 2 = adc_val / 65535 * V_ref
		# (3300 * 2 * battery.value) >> 16
		voltage = (3300 * self.my_bat_voltage_sense.value) >> 15
		i = (voltage - BATTERY_LIMIT) // BATTERY_DELTA
		i = max(0, min(len(BATVOLT_TO_PERCENT) - 1, i))
		return BATVOLT_TO_PERCENT[i]

	def sleep(self) -> None:
		self.my_keymatrix.deinit()
		rows = list()
		cols = list()
		for pin in MATRIX_ROWS:
			io = digitalio.DigitalInOut(pin)
			io.direction = digitalio.Direction.OUTPUT
			io.drive_mode = digitalio.DriveMode.PUSH_PULL
			io.value = 0
			rows.append(io)
		for pin in MATRIX_COLS:
			alarm_pin = alarm.pin.PinAlarm(pin, value=False, pull=True)
			cols.append(alarm_pin)
		alarm.exit_and_deep_sleep_until_alarms(cols, preserve_dios=rows)

	def is_charging(self) -> bool:
		return not self.my_charging_sense.value

	def poweroff(self) -> None:
		if supervisor.runtime.usb_connected:
			# DO NOT poweroff(disconnect battery) when USB is connected!
			return
		pin = digitalio.DigitalInOut(board.BATTERY_ENABLE)
		# it should be powered off already, but let's finish this
		pin.switch_to_output()
		# set 0 to set NAND output to 1, thus SYS_OFF becomes 1, battery disconnected
		pin.value = 0
		# restart the board if it's still on
		import microcontroller
		microcontroller.reset()
