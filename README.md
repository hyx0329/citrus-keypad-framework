# Citrus Keypad framework

A solid keyboard framework based on CircuitPython.

Tested on nRF52840 and RP2040, with CircuitPython 9.

Key features:

- TapEngine powered
    - multi-layer keymap, order-free
        - feels like popular keyboard firmware, but with MORE flexiblity
    - different actions for short & long & super long press
        - of course, with adjustable preferences
    - tap dance
- Anything can be a "keycode" in the key map
    - any objects, functions, whatever,
    - standard keycodes are processed and sent via HID interfaces
    - arbitrary functions can be executed with no pain
    - users can easily add more arbitrary "keycode"
- Optional NKRO keyboard
    - both USB and BLE
- Optional absolute mouse
    - both USB and BLE
