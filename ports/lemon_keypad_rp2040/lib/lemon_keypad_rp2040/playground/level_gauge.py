# Here we have implemented some example user functions
import os
import asyncio
import math
from ulab import numpy as np

try:
	from lemon_keypad_rp2040 import LemonKeypadRp2040
except ImportError:
	pass


async def level_gauge(dev: LemonKeypadRp2040) -> None:
	imu = dev.my_imu
	pixels = dev.my_pixels

	event_queue = dev.my_keypad.events

	led_positions = np.array([
		(np.cos((i * 360/pixels.n + 90) / 180 * math.pi), np.sin((i * 360/pixels.n + 90) / 180 * math.pi)) for i in range(pixels.n, 0, -1)
	])

	red = np.array((0x40, 0, 0))
	green = np.array((0, 0x40, 0))
	blue = np.array((0, 0, 0x40))

	imu_comp_vector = np.array((0, 0, 0))
	if (comp := os.getenv("imu_accel_comp_x")):
		imu_comp_vector[0] = comp * 0.0001
	if (comp := os.getenv("imu_accel_comp_y")):
		imu_comp_vector[1] = comp * 0.0001
	if (comp := os.getenv("imu_accel_comp_z")):
		imu_comp_vector[2] = comp * 0.0001

	x_base = 0
	y_base = 0

	while True:
		await asyncio.sleep(0)

		new_event = event_queue.get()
		if new_event is not None and new_event.pressed:
			if new_event.key_number == 0:
				x_base, y_base, _ = imu_comp_vector + imu.acceleration
			else:
				# clear and quit
				pixels.fill((0, 0, 0))
				return

		x1, y1, z1 = imu_comp_vector + imu.acceleration
		platform_vector = np.array((x1-x_base, y1-y_base))
		length = np.linalg.norm(platform_vector)
		if length < 0.27:
			pixels.fill(green.tolist())
			continue
		unit_vector = platform_vector / length
		factors = np.dot(led_positions, unit_vector)
		factors = np.array([factors]).transpose()
		colors = factors * red + (1 - factors) * blue
		pixels[:] = colors.tolist()
