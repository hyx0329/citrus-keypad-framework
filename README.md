# Citrus Keypad framework

A solid keyboard framework based on CircuitPython.

Tested on nRF52840 and RP2040, with CircuitPython 9. See `ports`.

Key features:

- Arbitrary code execution via "keycode" in key map
    - any objects, functions, whatever,
    - standard keycodes are processed and sent via HID interfaces
    - arbitrary functions can be executed with no pain
    - users can easily add support for any "keycode"
- TapEngine powered
    - multi-layer keymap, order-free
        - feels like popular keyboard firmware, but with MORE flexiblity
    - different actions for short & long & super long press
        - of course, with adjustable preferences
    - tap dance
- Optional NKRO keyboard
    - both USB and BLE
- Optional absolute mouse(like a touch panel)
    - both USB and BLE

## Profiling

Flexibility comes with costs. Writing high performance code is feasible but
will make the code harder to maintain & reuse. Limitations:

- key response time: ~30ms
    - debounce by keypad module: 20ms(adjustable)
    - process time: from 5ms to 30ms
- higher power consumption
    - always polling
- startup time: ~5 seconds
    - ~3 seconds if code precompiled to mpy

It's definitely suitable for USB-powered macro pads though.
