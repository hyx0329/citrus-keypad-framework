# Citrus Keypad framework

─=≡Σ((( つ•̀ω•́)つ

A flexible keyboard framework, targeting CircuitPython-based macro pads.

Key features:

- Async event processing
- Arbitrary keycodes including function calls
- Flexible multi-layer action map/keymap support
- NKRO keyboard and absolute mouse(like a touch panel)
- Built-in basic BLE support

Developed and tested on nRF52840 and RP2040 with CircuitPython 9.

## Foreword

This project is published in the sole hope that it will be useful to someone. If you think it deserves, do not hesitate to give it a star (・ω< )☆

## Project structure

- `lib`: Precompiled dependencies from existing library bundles.
- `lib.local`: Locally-developed libs, which only contains `citrus_keypad`(the framework) at the moment.
- `stubs`: `download_stubs.sh` will download and unpack py version of bundles to here to enable proper code completion in VSCode.
- `ports`: Code for specific devices. This includes per-device framework overrides and some useful stuff.
- `compile.sh`: A script to compile py files to mpy files.
- `deploy.sh`: A script to deploy all resource files for a port to a specific folder.
- `circup.sh`: A simple wrapper of circup for easier access.

This project uses virtual environment managed by `uv` to provide a consistent workspace.

## Some implementation details

### Action map(keymap) and TapEngine

The multi-layer action map is based on a submodule named `TapEngine`. It originates from my third attempt to implement a Python-based keyboard firmware.

`TapEngine` handles following things:

- Read key input events using user provided event getter, which is a normal function that returns [`keypad.Event`](https://circuitpython.readthedocs.io/en/latest/shared-bindings/keypad/index.html#keypad.Event) or None.
- Process the key event by looking up the action map provided by the user, and then determine the actual action to perform.
    - If it's internal or special actions(like `CompositeAction`, `TapDance`), it will be handles internally, as the actual action is to be determined.
    - Otherwise the actual action will be passed to the actual action processor.
- The actual action is sent to the user-provided action event handler. The handler will decide whether to send a key press or trigger another arbitrary function, etc..

There are 2 special actions provided to the users:

- `CompositeAction`: The real action is determined by how long the key is pressed. Users can customize short tap action, hold action(and layer change at the same time), and super long hold action, and their timings. The priority preference to trigger tap or hold action can also be customized.
- `TapDance`: The real action is determined by how many times key is pressed. Users can configure a tap interval, before which if a new tap is arrived, the real action becomes the next one. `TapDance` can contain other special actions.

The action map(keymap) is a dictionary like `{layer ID: sequence of actions}`. This sequence of actions is basically a list with length of the number of keys. The action can be a `CompositeAction`, `TapDance`, or an arbitrary action(even a function).

The order of layers is tracked in a stack, and the overlay order is NOT affected by layer ID order. When a new layer is activated, it will be put directly above last layer.

### HID overrides, USB and BLE interface

The HID interfaces provided by adafruit are modified a bit to make them compatible with async runtime.

NKRO keyboard and absolute mouse are both implemented for USB and BLE interfaces.

### Keycodes

Integers are treated as keyboard keycodes. Mouse and consumer control codes are wrapped in simple subclasses of `int` defined at `lib.local/citrus_keypad/keycode.py`.

The default implementation of key action handler handles `int` instances and callables. The `int` instances are interpreted as keycodes, and callables are executed with current keyboard instance being the first parameter.

As a result, users can use anything aside from `int` and callables as custom actions.

However, users can override the default action handler and take full control if desired.

Read current ports for more details and examples.

## Performance

Flexibility comes with costs. Writing high performance code is feasible but
will make the code harder to maintain & reuse. Known limitations:

- key response time: ~30ms(or even longer)
    - debounce by keypad module: 20ms(adjustable)
    - process time: from 5ms to 30ms
- maybe higher power consumption
    - always polling
    - my Makerdiary nRF52840 dongle: 8mA/5V
        - device idle current is 3mA/5V
        - uses DCDC convertor
    - my Lemon Keypad RP2040: 35mA/5V
        - uses AMS1117 LDO
- slow startup time: ~5 seconds
    - ~3 seconds if code precompiled to mpy

It's definitely suitable for USB-powered macro pads though.

## Q&As

### Why named `Citrus Keypad framework`?

It was for my customized Lemon Keypad, as an enhanced version of software. Lemon is citrus, so the enhanced version uses the name.

### License?

I haven't decided yet. All rights reserved. I'm open to suggestions.
