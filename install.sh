#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Ensure the script is run with superuser (root) privileges
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script as root (use sudo)"
  exit 1
fi

# Define variables
PROGRAM_NAME="hex648.py"
ASSEMBLY_FILE="hex64hash.c"
SHARED_LIB="hex64hash.so"
BIN_PATH="/usr/bin"
LIB_PATH="/usr/lib"
CONF_PATH="/etc/ld.so.conf.d/hex64.conf"
COMMAND_NAME="hex64"

# Check for necessary files
if [ ! -f "$PROGRAM_NAME" ]; then
  echo "Error: $PROGRAM_NAME not found in the current directory."
  exit 1
fi

if [ ! -f "$ASSEMBLY_FILE" ]; then
  echo "Error: $ASSEMBLY_FILE not found in the current directory."
  exit 1
fi

# Compile the shared library
echo "Compiling $ASSEMBLY_FILE into a shared library..."
gcc -shared -o "$LIB_PATH/$SHARED_LIB" -fPIC "$ASSEMBLY_FILE"
if [[ $? -ne 0 ]]; then
  echo "Error: Failed to compile the shared library."
  exit 1
fi
echo "Shared library created: $LIB_PATH/$SHARED_LIB"

# Ensure the shared library can be found by the system
echo "Linking shared library to $CONF_PATH..."
echo "$LIB_PATH" > "$CONF_PATH"
ldconfig

# Install the Python script as a system-wide command
echo "Installing $PROGRAM_NAME as $COMMAND_NAME..."
cp "$PROGRAM_NAME" "$BIN_PATH/$COMMAND_NAME"
chmod +x "$BIN_PATH/$COMMAND_NAME"

# Add a shebang to the Python script if not present
if ! head -n 1 "$BIN_PATH/$COMMAND_NAME" | grep -q "^#!"; then
  echo "Adding shebang to $BIN_PATH/$COMMAND_NAME..."
  sed -i '1i#!/usr/bin/env python3' "$BIN_PATH/$COMMAND_NAME"
fi

echo "Installation complete! You can now run the program using the command: $COMMAND_NAME"
