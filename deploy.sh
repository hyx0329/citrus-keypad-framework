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
sync -f "$TARGET_DIR/code.py"
