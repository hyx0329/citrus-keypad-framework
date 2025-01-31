import os
import microcontroller
import storage
import supervisor
import usb_hid


### handle safe mode ###

# CHANGEME: when porting to other devices
# The exception should block further code execution on an incompatible device
def should_enter_safemode() -> bool:
	# TODO: implement safemode switch
	return False


if should_enter_safemode():
	microcontroller.on_next_reset(microcontroller.RunMode.SAFE_MODE)
	microcontroller.reset()


### handle configs ###

# Update USB drive label on demand, up to 11 chars(FAT filesystem)
DRIVE_LABEL = os.getenv('drive_label')
if DRIVE_LABEL is None:
	pass
elif (label := DRIVE_LABEL.upper()) != storage.getmount("/").label:
	# FAT labels are uppercase
	storage.remount("/", readonly=False)
	m = storage.getmount("/")
	m.label = label
	storage.remount("/", readonly=True)

# Lock USB drive to protect from host writing
if os.getenv('lock_usb_drive') or ('lock_usb_drive.txt' in os.listdir('/')):
	# make it read-write for CPY, so it'll become read-only for host because of the concurrent write protection
	storage.remount('/', readonly=False)

# Disable serial console. NOT RECOMMENDED FOR ROOKIES.
# Read https://learn.adafruit.com/customizing-usb-devices-in-circuitpython/circuitpy-midi-serial#usb-serial-console-repl-and-data-3096590-12
if os.getenv('disable_serial_console'):
	import usb_cdc
	usb_cdc.disable()

# Disable mass storage interface, and MIDI, so almost looks like a regular keypad.
if os.getenv('disable_usb_drive') or ('disable_usb_drive.txt' in os.listdir('/')):
	storage.disable_usb_drive()
if os.getenv('disable_midi'):
	import usb_midi
	usb_midi.disable()

# Setting up HID interface in advance
hid_devices = [usb_hid.Device.KEYBOARD, usb_hid.Device.MOUSE, usb_hid.Device.CONSUMER_CONTROL]
if os.getenv('use_nkro_keyboard'):
	from citrus_keypad.hid_helper.device_builder.nkro_keyboard import new_device
	hid_devices[0] = new_device()
if os.getenv('use_absolute_mouse'):
	from citrus_keypad.hid_helper.device_builder.absolute_mouse import new_device
	hid_devices[1] = new_device()
usb_hid.enable(hid_devices)

### Extra environment setup ###

# Ensure default BLE workflow disabled, so the python program can take over it.
try:
	supervisor.runtime.ble_workflow = False
except NotImplementedError:
	pass
