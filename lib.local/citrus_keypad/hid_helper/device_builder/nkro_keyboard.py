import usb_hid

# Report ID 0x4
# modifiers report byte count: 1, 8bits,
# keys report byte count: 16, 128bits, maximum 128keys
# fmt: off
def new_device(report_id: int = 12):
	return usb_hid.Device(
		report_descriptor=bytes((
			0x05, 0x01,                     # Usage Page (Generic Desktop),
			0x09, 0x06,                     # Usage (Keyboard),

			0xA1, 0x01,                     # Collection (Application),
			0x85, report_id,                # Report ID  (default 12, set at RUNTIME),

			# LED output report, see Universal Serial Bus HID Usage Tables section 11 and 11.1
			# keyboard has total 6 available LEDs
			# first 5, num lock, caps lock, scroll lock, compose, kana
			0x05, 0x08,                     #   Usage Page (LEDs),
			0x19, 0x01,                     #   Usage Minimum (1),
			0x29, 0x05,                     #   Usage Maximum (5),
			0x95, 0x05,                     #   Report Count (5),
			0x75, 0x01,                     #   Report Size (1 bit each),
			0x91, 0x02,                     #   Output (Data, Variable, Absolute),
			# padding, pad one bit, so IDs aligned
			0x95, 0x01,                     #   Report Count (1),
			0x75, 0x01,                     #   Report Size (1 bit each),
			0x91, 0x03,                     #   Output (Constant),
			# last one, Shift(used in JP layout), with ID 7
			0x05, 0x08,                     #   Usage Page (LEDs),
			0x19, 0x07,                     #   Usage Minimum (7),
			0x29, 0x07,                     #   Usage Maximum (7),
			0x95, 0x05,                     #   Report Count (1),
			0x75, 0x01,                     #   Report Size (1 bit each),
			0x91, 0x02,                     #   Output (Data, Variable, Absolute),
			# padding, pad one bit, so aligned to 1 byte
			0x95, 0x01,                     #   Report Count (1),
			0x75, 0x01,                     #   Report Size (1 bit each),
			0x91, 0x03,                     #   Output (Constant),


			# modifiers input report, bitmap, 1 byte
			0x05, 0x07,                     #   Usage Page (Key Codes),
			0x19, 0xE0,                     #   Usage Minimum (224),
			0x29, 0xE7,                     #   Usage Maximum (231),
			0x95, 0x08,                     #   Report Count (8),
			0x75, 0x01,                     #   Report Size (1 bit each),
			0x15, 0x00,                     #   Logical Minimum (0),
			0x25, 0x01,                     #   Logical Maximum (1),
			0x81, 0x02,                     #   Input (Data, Variable, Absolute),

			# keys input report, bitmap, 15 bytes
			0x05, 0x07,                     #   Usage Page (Key Codes),
			0x19, 0x00,                     #   Usage Minimum (0),
			0x29, 15*8-1,                   #   Usage Maximum (15*8-1),
			0x95, 15*8,                     #   Report Count (15*8),
			0x75, 0x01,                     #   Report Size (1 bit each),
			0x15, 0x00,                     #   Logical Minimum (0),
			0x25, 0x01,                     #   Logical Maximum(1),
			0x81, 0x02,                     #   Input (Data, Variable, Absolute),

			0xc0                            # End Collection (Application),
		)),
		usage_page=0x01,
		usage=0x06,
		report_ids=(report_id,),
		# 1 byte for modifiers(8 keys), 15 bytes for rest keys(120 keys, though not all used)
		in_report_lengths=(16,),
		out_report_lengths=(1,),
	)
# fmt: on
