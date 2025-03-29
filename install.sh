#!/bin/bash

set -e

if [ "$EUID" -ne 0 ]; then
  echo "Please run this script as root (use sudo)"
  exit 1
fi

PROGRAM_NAME="hex648.py"
ASSEMBLY_FILE="hex64hash.c"
SHARED_LIB="libhex64hash.so"  # Added 'lib' prefix
BIN_PATH="/usr/bin"
LIB_PATH="/usr/lib"
CONF_PATH="/etc/ld.so.conf.d/hex64.conf"
COMMAND_NAME="hex64"

# Check for required files
[ ! -f "$PROGRAM_NAME" ] && echo "Error: $PROGRAM_NAME missing!" && exit 1
[ ! -f "$ASSEMBLY_FILE" ] && echo "Error: $ASSEMBLY_FILE missing!" && exit 1

# Compile shared library with correct naming
echo "Compiling shared library..."
gcc -shared -fPIC -o "$SHARED_LIB" "$ASSEMBLY_FILE"
if [ $? -ne 0 ]; then
  echo "Compilation failed. Ensure gcc is installed."
  exit 1
fi

# Install library and update linker
echo "Installing library to $LIB_PATH..."
install -m 644 "$SHARED_LIB" "$LIB_PATH/"
echo "$LIB_PATH" > "$CONF_PATH"
ldconfig

# Install script
echo "Installing hex64 command..."
install -m 755 "$PROGRAM_NAME" "$BIN_PATH/$COMMAND_NAME"

# Add shebang if missing
if ! grep -q "^#!/usr/bin/env python3" "$BIN_PATH/$COMMAND_NAME"; then
  sed -i '1i#!/usr/bin/env python3' "$BIN_PATH/$COMMAND_NAME"
fi

echo "Installation complete. Use: hex64 --help"
