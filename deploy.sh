#!/usr/bin/env bash

DEFAULT_PORT="pca10059"
DEFAULT_DIR="build"

set -e

TARGET_DIR=$1
TARGET_DIR=${TARGET_DIR:-$DEFAULT_DIR}
TARGET_PORT=${2:-$DEFAULT_PORT}

[ -d "$TARGET_DIR" ] || mkdir -p "$TARGET_DIR"

rsync -r --times lib/ "$TARGET_DIR/lib/"
rsync -r --times lib.local/ "$TARGET_DIR/lib/"
rsync -r --times -f'- *requirements.txt' "ports/$TARGET_PORT/" "$TARGET_DIR/"

EXTRA="ports/$TARGET_PORT/extra-requirements.txt"

if [ -f "$EXTRA" ]; then
    # install extra libs
    mkdir -p build
    cp boot_out.txt build
    circup --path build install -r "$EXTRA"
    rsync -r --times build/lib/ "$TARGET_DIR/lib/"
fi

sync -f "$TARGET_DIR/code.py"
