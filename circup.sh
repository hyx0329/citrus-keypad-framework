#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

[ -e "$SCRIPT_DIR/boot_out.txt" ] || exit 1

circup --path "$SCRIPT_DIR" "$@"
