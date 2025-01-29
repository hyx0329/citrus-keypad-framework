from micropython import const

DESCRIPTOR = const((
	b"\x05\x0C"  # Usage Page (Consumer)
	b"\x09\x01"  # Usage (Consumer Control)
	b"\xA1\x01"  # Collection (Application)
	b"\x85\x03"  #   Report ID (3)
	b"\x75\x10"  #   Report Size (16)
	b"\x95\x01"  #   Report Count (1)
	b"\x15\x01"  #   Logical Minimum (1)
	b"\x26\x8C\x02"  #   Logical Maximum (652)
	b"\x19\x01"  #   Usage Minimum (Consumer Control)
	b"\x2A\x8C\x02"  #   Usage Maximum (AC Send)
	b"\x81\x00"  #   Input (Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
	b"\xC0"  # End Collection
))
