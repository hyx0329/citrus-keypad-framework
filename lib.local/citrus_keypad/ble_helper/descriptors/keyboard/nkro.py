from micropython import const

DESCRIPTOR = const((
	b"\x05\x01"                   # Usage Page (Generic Desktop),
	b"\x09\x06"                   # Usage (Keyboard),

	b"\xA1\x01"                   # Collection (Application),
	b"\x85\x01"                   # Report ID  (1),

	# LED output report, see Universal Serial Bus HID Usage Tables section 11 and 11.1
	# keyboard has total 6 available LEDs
	# first 5, num lock, caps lock, scroll lock, compose, kana
	b"\x05\x08"                   #   Usage Page (LEDs),
	b"\x19\x01"                   #   Usage Minimum (1),
	b"\x29\x05"                   #   Usage Maximum (5),
	b"\x95\x05"                   #   Report Count (5),
	b"\x75\x01"                   #   Report Size (1 bit each),
	b"\x91\x02"                   #   Output (Data, Variable, Absolute),
	# padding, align to 1 byte
	b"\x95\x01"                   #   Report Count (1),
	b"\x75\x03"                   #   Report Size (3 bit each),
	b"\x91\x03"                   #   Output (Constant),

	# modifiers input report, bitmap, 1 byte
	b"\x05\x07"                   #   Usage Page (Key Codes),
	b"\x19\xE0"                   #   Usage Minimum (224),
	b"\x29\xE7"                   #   Usage Maximum (231),
	b"\x95\x08"                   #   Report Count (8),
	b"\x75\x01"                   #   Report Size (1 bit each),
	b"\x15\x00"                   #   Logical Minimum (0),
	b"\x25\x01"                   #   Logical Maximum (1),
	b"\x81\x02"                   #   Input (Data, Variable, Absolute),

	# keys input report, bitmap, 15 bytes
	b"\x05\x07"                   #   Usage Page (Key Codes),
	b"\x19\x00"                   #   Usage Minimum (0),
	b"\x29\x77"                   #   Usage Maximum (15*8-1),
	b"\x95\x78"                   #   Report Count (15*8),
	b"\x75\x01"                   #   Report Size (1 bit each),
	b"\x15\x00"                   #   Logical Minimum (0),
	b"\x25\x01"                   #   Logical Maximum(1),
	b"\x81\x02"                   #   Input (Data, Variable, Absolute),

	b"\xc0"                            # End Collection (Application),
))
