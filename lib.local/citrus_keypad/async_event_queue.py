import asyncio


class AsyncEventQueue:
	# Helper class which moves the polling burden from Python code to underlying C code
	# Reference: https://github.com/adafruit/circuitpython/pull/6712
	# and https://github.com/adafruit/circuitpython/issues/8412

	def __init__(self, events):
		self._events = events

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		pass

	async def __await__(self):
		await asyncio.core._io_queue.queue_read(self._events)
		return self._events.get()

	def __aiter__(self):
		return self

	async def __anext__(self):
		await asyncio.core._io_queue.queue_read(self._events)
		return self._events.get()
