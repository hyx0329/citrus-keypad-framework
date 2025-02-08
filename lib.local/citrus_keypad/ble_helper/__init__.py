import os

from _bleio import Address
import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard import BatteryService
from adafruit_ble.services.standard.device_info import DeviceInfoService

from .descriptors.consumer_control import DESCRIPTOR as CC_DESC


# TODO: make it switchable
if os.getenv('use_nkro_keyboard'):
	from .descriptors.keyboard.nkro import DESCRIPTOR as KB_DESC
else:
	from .descriptors.keyboard.standard import DESCRIPTOR as KB_DESC

# TODO: make it switchable
if os.getenv('use_absolute_mouse'):
	from .descriptors.mouse.absolute import DESCRIPTOR as MS_DESC
else:
	from .descriptors.mouse.standard import DESCRIPTOR as MS_DESC

try:
	from typing import Optional
except ImportError:
	pass

# Due to circuitpython's limitation, HID report will be send to ALL active connections.
# So only one active connection should be preserved.
# Reed https://github.com/adafruit/circuitpython/blob/c3989b28e1858cfbf3d86806b711ae969c5e53ea/ports/nordic/common-hal/_bleio/Characteristic.c#L177
# Here only one host is connected.
class BleHelper:
	def __init__(self):
		self.hid = HIDService(hid_descriptor=KB_DESC + MS_DESC + CC_DESC)
		# TODO: make battery info optional?
		self.battery = BatteryService()
		self.battery.level = 100

		self.advertisement = ProvideServicesAdvertisement(self.hid, self.battery)
		# Advertise as "Keyboard" (0x03C1) icon when pairing
		# https://www.bluetooth.com/specifications/assigned-numbers/
		self.advertisement.appearance = 961

		self.scan_response = Advertisement()
		self.scan_response.complete_name = "Citrus Keypad"

		self.device_info = DeviceInfoService(software_revision="0.1.0-rc1", manufacturer="Citrus CLUB")

		self.ble = adafruit_ble.BLERadio()

	@property
	def advertise_name(self) -> str:
		return self.scan_response.complete_name

	@advertise_name.setter
	def advertise_name(self, value: str):
		self.scan_response.complete_name = value

	@property
	def devices(self) -> list:
		return self.hid.devices

	@property
	def battery_level(self) -> int:
		return self.battery.level

	@battery_level.setter
	def battery_level(self, value: int):
		self.battery.level = value

	@property
	def connected(self):
		return self.ble.connected

	@property
	def connections(self):
		return self.ble.connections

	def start_advertising(self):
		# The advertisement is automatically stopped when there's a new connection.
		self.ble.start_advertising(self.advertisement, self.scan_response)

	def start_advertising_advanced(self, *, connectable: bool = False,
											anonymous: bool = True,
											interval: float = 0.1,
											timeout: Optional[int] = None,
											tx_power: int = 0,
        									directed_to: Optional[Address] = None):
		# NOTE: only connectable connection can use directed advertising
		advertisement_bytes = bytes(self.advertisement)
		scan_response_bytes = bytes(self.scan_response)
		self.ble._adapter.start_advertising(
				advertisement_bytes,
				scan_response=scan_response_bytes,
				connectable=connectable,
				anonymous=anonymous,
				interval=interval,
				tx_power=tx_power,
				timeout=0 if timeout is None else timeout,
				directed_to=directed_to
			)

	def stop_advertising(self):
		self.ble.stop_advertising()

	@property
	def advertising(self):
		return self.ble.advertising

	def disconnect_all(self):
		for c in self.ble.connections:
			c.disconnect()
