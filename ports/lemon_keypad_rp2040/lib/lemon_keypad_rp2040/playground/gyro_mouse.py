import asyncio
import math
from ulab.numpy.linalg import norm
from citrus_keypad.keycode import M_LEFT, M_RIGHT, M_MIDDLE

try:
	from lemon_keypad_rp2040 import LemonKeypadRp2040
except ImportError:
	pass


async def gyro_mouse(dev: LemonKeypadRp2040) -> None:

	# set pixels, indicated program is running

	pixels = dev.my_pixels
	imu = dev.my_imu
	event_queue = dev.my_keypad.events

	pixels.fill((0, 0x16, 0x16))
	sensitivity = 1.5

	key_map = {
		2: M_LEFT,
		3: M_MIDDLE,
		4: M_RIGHT,
	}

	while True:
		await asyncio.sleep(0)

		new_event = event_queue.get()
		if new_event is not None:
			# make mouse key inputs
			if new_event.key_number in key_map:
				await dev.handle_key_action(new_event.pressed, key_map[new_event.key_number])
			elif new_event.pressed:
				if new_event.key_number == 1:
					# increase sensitivity
					sensitivity += 0.1
					sensitivity = min(3, sensitivity)
				elif new_event.key_number == 5:
					# decrease sensitivity
					sensitivity -= 0.1
					sensitivity = max(0.3, sensitivity)
				elif new_event.key_number == 0:
					# clear pixels and quit
					pixels.fill((0, 0, 0))
					return

		# The gyro only gives angular rates, not absolute values to original position
		dx, _, dz = imu.gyro

		# linear values
		# mouse_x = -dz * 10 * sensitivity
		# mouse_y = -dx * 10 * sensitivity

		# dynamic accleration, log
		# ensure x y acceleration same
		accel = math.log(abs(norm((dz, dx))) + 1)
		# clamp
		accel = min(40, accel)
		accel = max(1, accel)
		mouse_x = -dz * 10 * sensitivity * accel
		mouse_y = -dx * 10 * sensitivity * accel

		dev.current_hid_agent.mouse_move(int(mouse_x), int(mouse_y))

		# print("dz: %.2f, dx: %.2f, mouse_x: %.2f, mouse_y: %.2f, accel: %.2f, sensitivity: %.2f" % (dz, dx, mouse_x, mouse_y, accel, sensitivity))
