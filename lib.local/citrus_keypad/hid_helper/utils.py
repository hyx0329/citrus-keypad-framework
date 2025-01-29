try:
	from typing import Sequence
except Exception:
	pass


def find_device(
	devices: Sequence[object],
	*,
	usage_page: int,
	usage: int,
) -> object:
	if hasattr(devices, "send_report"):
		devices = [devices]  # type: ignore
	device = None
	for dev in devices:
		if (
			dev.usage_page == usage_page
			and dev.usage == usage
			and hasattr(dev, "send_report")
		):
			device = dev
			break
	if device is None:
		raise ValueError("Could not find matching HID device.")

	return device
