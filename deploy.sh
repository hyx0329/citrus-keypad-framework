#!/usr/bin/env bash

set -e

target=$1
target=${target:-build}

[ -d "$target" ] || mkdir -p "$target"

rsync -r --times lib code.py boot.py safemode.py settings.toml "$target/"
rsync -r --times -f'- lemon_keypad_rp2040' lib.local/ "$target/lib/"
# rsync -r --times assets/ "$target/"
sync -f "$target/code.py"
