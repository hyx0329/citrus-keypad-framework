def is_coroutine(obj):
	# This is the only we have on CircuitPython
	if obj.__class__.__name__ is "coroutine":  # noqa: F632
		return True
	return False
