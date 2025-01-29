from micropython import const

DESCRIPTOR = const((
	# Absolute mouse
	b"\x05\x01"       # Usage Page (Generic Desktop)
	b"\x09\x02"       # Usage (Mouse)

	b"\xA1\x01"       # Collection (Application)
	b"\x09\x01"       # Usage (Pointer)

	b"\xA1\x00"       # Collection (Physical)
	b"\x85\x02"       # Report ID  (2)

	# Buttons
	b"\x05\x09"       # Usage Page (Button)
	b"\x19\x01"       # Usage Minimum (0x01)
	b"\x29\x05"       # Usage Maximum (0x05)
	b"\x15\x00"       # Logical Minimum (0)
	b"\x25\x01"       # Logical Maximum (1)
	b"\x95\x05"       # Report Count (5)
	b"\x75\x01"       # Report Size (1)
	b"\x81\x02"       # Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
	b"\x75\x03"       # Report Size (3)
	b"\x95\x01"       # Report Count (1)
	b"\x81\x03"       # Input (Const,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)

	# Movement
	b"\x05\x01"       # Usage Page (Generic Desktop Ctrls)
	b"\x09\x30"       # Usage (X)
	b"\x09\x31"       # Usage (Y)
	b"\x15\x00"       # Logical Minimum (0)
	b"\x26\xFF\x7F"   # Logical Maximum (32767)
	# b"\x35\x00"       # Physical Minimum (0)
	# b"\x46\xff\x7f"   # Physical Maximum (32767)
	b"\x75\x10"       # Report Size (16)
	b"\x95\x02"       # Report Count (2)
	b"\x81\x02"       # Input (Data,Var,Rel,No Wrap,Linear,Preferred State,No Null Position)

	# Wheel
	b"\x09\x38"       # Usage (Wheel)
	b"\x15\x81"       # Logical Minimum (-127)
	b"\x25\x7F"       # Logical Maximum (127)
	# "\x35\x81"        # Physical Minimum (same as logical)
	# "\x45\x7f"        # Physical Maximum (same as logical)
	b"\x75\x08"       # Report Size (8)
	b"\x95\x01"       # Report Count (1)
	b"\x81\x06"       # Input (Data,Var,Rel,No Wrap,Linear,Preferred State,No Null Position)

	b"\xC0"        # End Collection (Physical)
	b"\xC0"        # End Collection (Application)
))
