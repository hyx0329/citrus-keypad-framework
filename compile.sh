#!/usr/bin/env bash

source_dir=${1:-lib.local}
# remove trailing slash
source_dir=${source_dir%/}

MPY_CROSS=${MPY_CROSS:-mpy-cross}
OUTPUT_DIR=build/lib

set -e

while read -r SOURCE; do
    file_path=${SOURCE#$source_dir/}
    parents=${file_path%/*}
    mpy_file_path=${file_path/.py/.mpy}
    mkdir -p "$OUTPUT_DIR/$parents"
    "$MPY_CROSS" -o "$OUTPUT_DIR/$mpy_file_path" -- "$SOURCE"
done <<< $(find "$source_dir" -name "*.py")
