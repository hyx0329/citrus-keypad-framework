import os
import adafruit_logging as logging


logger = logging.getLogger("ErrorCatcher")


if os.getenv('debug'):
	logger.setLevel(logging.DEBUG)
else:
	logger.setLevel(logging.WARNING)


def no_fail_tag(tag: str):
	def no_fail(func):
		def wrapper(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except Exception as e:
				logger.debug('Ignore exception(%s): %s: %s', tag, e.__class__.__name__, e)
				return None
		return wrapper
	return no_fail


def no_fail(func):
	def wrapper(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except Exception as e:
			logger.debug('Ignore exception: %s: %s', e.__class__.__name__, e)
			return None
	return wrapper
