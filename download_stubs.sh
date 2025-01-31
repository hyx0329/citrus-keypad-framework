#!/usr/bin/env bash

CPY_BUNDLE_DATE=20241127
CPY_BUNDLE_COMMUNITY_DATE=20241110
CPY_BUNDLE=https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/${CPY_BUNDLE_DATE}/adafruit-circuitpython-bundle-py-${CPY_BUNDLE_DATE}.zip
CPY_BUNDLE_COMMUNITY=https://github.com/adafruit/CircuitPython_Community_Bundle/releases/download/${CPY_BUNDLE_COMMUNITY_DATE}/circuitpython-community-bundle-py-${CPY_BUNDLE_COMMUNITY_DATE}.zip

mkdir stubs
cd stubs


curl -fsSL -o cpy-bundle-py.zip "${CPY_BUNDLE}"
curl -fsSL -o cpy-bundle-community-py.zip "${CPY_BUNDLE_COMMUNITY}"

unzip cpy-bundle-py.zip
unzip cpy-bundle-community-py.zip

mv adafruit-circuitpython-bundle-py-${CPY_BUNDLE_DATE} adafruit-circuitpython-bundle-py
mv circuitpython-community-bundle-py-${CPY_BUNDLE_COMMUNITY_DATE} circuitpython-community-bundle-py
