# ePass Flasher

A Python-based firmware flashing tool for ePass devices with automatic device tree patching and SPI NAND flash support.

## Overview

ePass Flasher is a comprehensive tool that:
- **Patches device trees** dynamically based on device configuration
- **Flashes firmware** to SPI NAND flash memory via FEL mode
- **Auto-detects flash size** and adjusts partition layouts accordingly
- **Supports multiple device versions** (0.2, 0.3.1, etc.)

## Requirements

### System Requirements
- **Windows**: Windows 7 or later
- **Linux**: Modern distribution with USB access
- **Python**: Python 3.10 or higher

### Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `pydevicetree==0.0.13` - Device tree manipulation library

### External Tools (Included)
- **xfel** - FEL mode communication tool for Allwinner devices
- **dtc** - Device Tree Compiler

## Installation

1. **Clone or download** this repository to your local machine

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify** that all required files are present:
   - `xfel.exe` (Windows) or `xfel` binary (Linux)
   - `dtc.exe` (Windows) or `dtc` binary (Linux)
   - Device tree files in `dts/` directory
   - Configuration files in `configs/` directory
   - Required DLL files (Windows): `libusb-1.0.dll`, `libfdt-1.dll`, `libyaml-0-2.dll`

## Usage

### Preparing Your Device

1. **Enter FEL Mode** on your ePass device:
   - Power off the device
   - Press and hold the FEL button (specific to your device)
   - Connect via USB to your computer
   - Release the FEL button

2. **Verify FEL mode** by running:
   ```bash
   # Windows
   xfel.exe version
   
   # Linux
   xfel version
   ```

### Running the Flasher

1. **Place firmware files** in the same directory as the flasher:
   - `u-boot-sunxi-with-spl.bin` - Bootloader with SPL
   - `u-boot.img` - U-Boot image
   - `zImage-0.2` or `zImage-0.3` - Kernel image (version-specific)
   - `ubi.img` - Root filesystem (UBI format)

2. **Run the flasher**:
   ```bash
   python main.py
   ```

3. **Follow the interactive prompts**:
   - Select your device version (e.g., 0.2 or 0.3.1)
   - Review the configuration summary
   - Confirm to start flashing

4. **Wait for completion**:
   - The tool will automatically:
     - Detect flash size
     - Patch the device tree
     - Compile the device tree blob (DTB)
     - Erase the flash memory
     - Write bootloader, kernel, and filesystem
   
5. **Manually reboot** your device after the process completes

## Project Structure

```
epass_flasher/
├── main.py              # Main entry point
├── flasher.py           # Firmware flashing logic
├── dt_patcher.py        # Device tree patching engine
├── interact.py          # User interaction handler
├── configs/             # Device configuration files
│   ├── 0.2.py          # Configuration for version 0.2
│   └── 0.3.1.py        # Configuration for version 0.3.1
├── dts/                 # Device tree source files
│   ├── devicetree_0.2.dts
│   ├── devicetree_0.3.dts
│   └── append/          # Additional DTS fragments
├── tools/               # Helper tools
│   └── preprocess_dts.py
├── xfel.exe            # FEL communication tool (Windows)
├── dtc.exe             # Device Tree Compiler (Windows)
└── *.dll               # Required DLL files (Windows)
```

## Configuration

### Adding a New Device Version

1. **Create a configuration file** in `configs/` (e.g., `configs/0.4.py`):

```python
from pydevicetree import Devicetree
from pydevicetree.ast import *
import os, sys, subprocess

xfel_config = {
    "erase_nand": True,
    "erase_size": int(0x8000000),
    "splwrite": [
        [1024, 0, "u-boot-sunxi-with-spl.bin"]
    ],
    "write": [
        [0x20000, "u-boot.img"],
        [0x100000, "devicetree.dtb"],
        [0x120000, "zImage-0.4"],
        [0x680000, "ubi.img"]
    ]
}

dt_file = "dts/devicetree_0.4.dts"
patchlist = []

def patch():
    # Custom patching logic here
    config = "屏幕型号: Your Screen\n"
    # Auto-detect flash size and adjust partitions
    # ...
    return patchlist, dt_file, config

def fel():
    return xfel_config
```

2. **Create the device tree file** in `dts/` (e.g., `dts/devicetree_0.4.dts`)

3. **Place the version-specific kernel** (e.g., `zImage-0.4`)

### Device Tree Patching

The device tree patcher supports four operations:

1. **delete_node**: Remove a node from the device tree
   ```python
   ["delete_node", "/soc/spi@1c05000", "spi-nand@0"]
   ```

2. **insert_node**: Add a node from a DTS file
   ```python
   ["insert_node", "/soc/spi@1c05000", "dts/append/spi_node.dtsa"]
   ```

3. **delete_prop**: Remove a property from a node
   ```python
   ["delete_prop", "/soc/spi@1c05000", "status"]
   ```

4. **insert_prop**: Add a property to a node
   ```python
   ["insert_prop", "/soc/spi@1c05000", "status", StringList(["okay"])]
   ```

**Note**: Always delete existing nodes/properties before inserting new ones with the same name.

## Troubleshooting

### dtc Not Found (Linux)
Install device tree compiler:
```bash
# Debian/Ubuntu
sudo apt-get install device-tree-compiler

# Arch Linux
sudo pacman -S dtc

# Fedora
sudo dnf install dtc
```

## Advanced Usage

### Manual Device Tree Operations

```python
from dt_patcher import Patcher

patcher = Patcher()
patcher.generate_config("configs/0.2.py")
patcher.apply_patches()
patcher.export_devicetree("custom_devicetree.dts")
patcher.compile_devicetree("custom_devicetree.dts", "custom_devicetree.dtb")
```

### Manual FEL Commands

```bash
# Erase flash
xfel spinand erase 0 0x8000000

# Write SPL
xfel spinand splwrite 1024 0 u-boot-sunxi-with-spl.bin

# Write firmware
xfel spinand write 0x20000 u-boot.img
xfel spinand write 0x100000 devicetree.dtb
xfel spinand write 0x120000 zImage-0.2
xfel spinand write 0x680000 ubi.img
```

## Safety Warnings

⚠️ **IMPORTANT WARNINGS**:

- **Data Loss**: All data on the flash memory will be **permanently erased**
- **Backup First**: Always backup important data before flashing
- **Correct Version**: Using wrong firmware can brick your device
- **Power Stability**: Ensure stable power during flashing (use battery if available)
- **Do Not Interrupt**: Never disconnect or power off during flashing

### Device Tree Patching Process

1. Load base device tree from DTS file
2. Parse configuration file for device version
3. Auto-detect SPI NAND flash size via xfel
4. Calculate optimal partition sizes
5. Apply patches from patchlist (delete/insert nodes and properties)
6. Remove duplicate properties
7. Export patched tree to DTS
8. Compile DTS to DTB using dtc

### Flash Writing Process

1. Erase entire flash (optional, recommended)
2. Write SPL to offset 0 with special command (`splwrite`)
3. Write U-Boot, DTB, kernel, and rootfs sequentially
4. Each write is verified by xfel

### xfel Communication

xfel uses USB bulk transfers to communicate with Allwinner SoCs in FEL mode, providing:
- Memory read/write
- SPI NAND flash operations
- Boot commands
- Version/chip information

## Contributing

To contribute:
1. Add support for new device versions via configuration files
2. Improve device tree patching logic
3. Add error handling and recovery features
4. Create automated tests

## License

See [LICENSE](LICENSE) file for details.

## Credits

- **xfel**: FEL communication tool for Allwinner devices
- **pydevicetree**: Python device tree manipulation library
- **dtc**: Device Tree Compiler from devicetree.org
