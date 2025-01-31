async def _dummy(): pass
_type_awaitable = type(_dummy())

def is_awaitable(obj):
	return isinstance(obj, _type_awaitable)
