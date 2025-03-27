#!/bin/bash

sudo bash setup_hex64.sh
# Exit immediately if a command exits with a non-zero status
set -e

# Check if the script is run with superuser (root) privileges
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script as root (use sudo)"
  exit 1
fi

# Define variables
PROGRAM_NAME="hex648.py"  # Replace with your Python program file name
INSTALL_PATH="/usr/bin" # Preferred location for user-installed executables
COMMAND_NAME="hex64"     # Name of the command to execute the program

# Check for the program file in the current directory
if [ ! -f "$PROGRAM_NAME" ]; then
  echo "Error: $PROGRAM_NAME not found in the current directory."
  exit 1
fi

# Copy the program to the system-wide directory
echo "Copying $PROGRAM_NAME to $INSTALL_PATH/$COMMAND_NAME..."
cp "$PROGRAM_NAME" "$INSTALL_PATH/$COMMAND_NAME"

# Make the program executable
echo "Making $INSTALL_PATH/$COMMAND_NAME executable..."
chmod +x "$INSTALL_PATH/$COMMAND_NAME"

# Check if the program has a valid shebang (e.g., #!/usr/bin/env python3)
# If not, prepend the shebang to the file
if ! head -n 1 "$INSTALL_PATH/$COMMAND_NAME" | grep -q "^#!"; then
  echo "Adding shebang to $INSTALL_PATH/$COMMAND_NAME..."
  sed -i '1i#!/usr/bin/env python3' "$INSTALL_PATH/$COMMAND_NAME"
fi

# Verify installation
if command -v "$COMMAND_NAME" >/dev/null 2>&1; then
  echo "Installation complete! You can now run the program using the command: $COMMAND_NAME"
else
  echo "Error: The program was not installed successfully."
  exit 1
fi
source env/bin/activate
