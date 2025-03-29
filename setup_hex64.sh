---

### How It Works

1. **Shared Library Installation**:
   - The `hex64hash.so` library is compiled from `hex64hash.c` and installed to `/usr/lib`.
   - The library path is added to the system's dynamic linker configuration (`/etc/ld.so.conf.d/hex64.conf`), and `ldconfig` is run to refresh the linker cache.

2. **Python Script Installation**:
   - The `hex648.py` script is copied to `/usr/bin` and renamed to `hex64`.
   - A shebang (`#!/usr/bin/env python3`) is added to ensure the script runs with Python 3.

3. **System-Wide Accessibility**:
   - After installation, the `hex64` command can be run from any directory without requiring a virtual environment or the current working directory.

---

### Final Steps

1. Place all the updated files (`install.sh`, `hex648.py`, `hex64hash.c`) in the same directory.
2. Run the installation script:
   ```bash
   sudo bash install.sh
