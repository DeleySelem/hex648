#!/bin/bash

# Define filenames
ASSEMBLY_FILE="hex64hash.c"
SHARED_LIB_LINUX="hex64hash.so"
SHARED_LIB_WINDOWS="hex64hash.dll"
PYTHON_SCRIPT="hex648.py"

# Assembly code content
ASSEMBLY_CONTENT=$(cat << 'EOF'
#include <stdint.h>

void Hex64Hash(uint32_t *ctx) {
    uint32_t eax, ebx, ecx, edx, edi;

    // First quadrant processing
    eax = ctx[0];
    ebx = ctx[1];
    ecx = ctx[2];
    edx = ctx[3];

    eax += ebx;
    ecx ^= eax;
    ecx = (ecx << 7) | (ecx >> (32 - 7));
    edx += ecx;
    ebx ^= edx;
    ebx = (ebx >> 11) | (ebx << (32 - 11));
    eax += ebx;
    ecx ^= eax;
    ecx = (ecx << 13) | (ecx >> (32 - 13));
    edx += ecx;
    ebx ^= edx;
    ebx = (ebx >> 17) | (ebx << (32 - 17));

    ctx[0] = eax;
    ctx[1] = ebx;
    ctx[2] = ecx;
    ctx[3] = edx;

    // Second quadrant processing
    eax = ctx[4];
    ebx = ctx[5];
    ecx = ctx[6];
    edx = ctx[7];

    edi = eax + ebx;
    edi ^= ecx;
    edi = (edi << 5) | (edi >> (32 - 5));
    edx += edi;
    eax ^= edx;
    ebx = __builtin_bswap32(ebx);
    ecx += ebx;
    edx ^= ecx;
    edx = (edx >> 9) | (edx << (32 - 9));

    ctx[4] = eax;
    ctx[5] = ebx;
    ctx[6] = ecx;
    ctx[7] = edx;

    // Cross-mixing
    ctx[3] ^= eax;
    ctx[7] ^= ebx;
    ctx[1] += ecx;
    ctx[5] -= edx;
}
EOF
)

# Check for necessary tools
echo "Checking prerequisites..."
if ! command -v gcc &> /dev/null; then
    echo "Error: GCC is not installed. Please install GCC and try again."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed. Please install Python3 and try again."
    exit 1
fi

# Save the assembly code to a file
echo "Creating $ASSEMBLY_FILE..."
echo "$ASSEMBLY_CONTENT" > $ASSEMBLY_FILE

# Compile the assembly code into a shared library
echo "Compiling $ASSEMBLY_FILE into a shared library..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    gcc -shared -o $SHARED_LIB_LINUX -fPIC $ASSEMBLY_FILE
    if [[ $? -ne 0 ]]; then
        echo "Error: Failed to compile the shared library."
        exit 1
    fi
    echo "Shared library created: $SHARED_LIB_LINUX"
elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* ]]; then
    gcc -shared -o $SHARED_LIB_WINDOWS -fPIC $ASSEMBLY_FILE
    if [[ $? -ne 0 ]]; then
        echo "Error: Failed to compile the shared library."
        exit 1
    fi
    echo "Shared library created: $SHARED_LIB_WINDOWS"
else
    echo "Error: Unsupported operating system. Only Linux and Windows are supported."
    exit 1
fi

# Create a virtual environment for Python
echo "Setting up Python virtual environment..."
python3 -m venv env
source env/bin/activate

# Install necessary Python dependencies (if any)
echo "Installing Python dependencies..."
pip install --upgrade pip setuptools
# Add additional dependencies below if required
# pip install <dependency>

# Deactivate the virtual environment
deactivate

echo "Setup complete!"
echo "To run your Python script, activate the virtual environment:"
echo "    source env/bin/activate"
echo "Then execute your Python script:"
echo "    python $PYTHON_SCRIPT"
