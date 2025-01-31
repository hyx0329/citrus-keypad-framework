# Makerdiary M60 keyboard

This is a preliminary port and is NOT tested on the real hardware, although I
have one.
I'd recommend to use ZMK(with patches) if it doesn't have to be Python.

The official documentation for advanced operations contains critical errors,
don't rely on that.

There's a NAND gate controlling M60's PMU(BQ24075)'s SYS_OFF pin.

Backlight is not implemented. I have some trouble understanding the original
implementation. Besides, the power consumption is just too high.
