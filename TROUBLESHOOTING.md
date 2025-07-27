# 🔧 Radiacode Home Assistant Integration - Troubleshooting Guide

## Common Installation Issues

### Issue: `bluepy` Build Failure

**Error Message:**
```
Unable to install package radiacode>=0.2.0: × Failed to build `bluepy==1.3.0`
error: [Errno 2] No such file or directory: 'make'
```

**Cause:** The `bluepy` library (required for Bluetooth support) needs to be compiled from source and requires build tools.

## Solutions

### Solution 1: Install Build Tools (Recommended)

**For Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install build-essential python3-dev libbluetooth-dev
pip install radiacode>=0.2.0
```

**For CentOS/RHEL/Fedora:**
```bash
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel bluez-libs-devel
pip install radiacode>=0.2.0
```

**For macOS:**
```bash
xcode-select --install
pip install radiacode>=0.2.0
```

### Solution 2: Use USB Only (Simplest)

If you don't need Bluetooth support, you can install the radiacode library without bluepy:

1. **Install only USB dependencies:**
   ```bash
   pip install usb
   ```

2. **Use USB connection only** during setup
3. **Skip Bluetooth configuration** in the integration setup

### Solution 3: Use Pre-compiled Wheels

**For Home Assistant OS:**
```bash
# Install system dependencies first
apk add --no-cache build-base python3-dev bluez-dev

# Then install radiacode
pip install radiacode>=0.2.0
```

**For Docker:**
```dockerfile
# Add to your Dockerfile
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libbluetooth-dev \
    && pip install radiacode>=0.2.0
```

### Solution 4: Alternative Installation Methods

**Using conda (if available):**
```bash
conda install -c conda-forge bluepy
pip install radiacode>=0.2.0
```

**Using system package manager:**
```bash
# Ubuntu/Debian
sudo apt install python3-bluepy

# Then install radiacode without bluepy
pip install radiacode>=0.2.0 --no-deps
pip install usb
```

## Platform-Specific Notes

### Linux
- **Ubuntu/Debian**: Install `build-essential` and `libbluetooth-dev`
- **CentOS/RHEL**: Install `Development Tools` group and `bluez-libs-devel`
- **Arch Linux**: Install `base-devel` and `bluez-libs`

### macOS
- **Requires Xcode Command Line Tools**: `xcode-select --install`
- **Bluetooth support limited**: May not work on all macOS versions

### Windows
- **Bluetooth not supported**: Use USB connection only
- **Install USB drivers**: May need Zadig for USB access

## Integration Setup

### USB Connection (Recommended for most users)
1. Connect your Radiacode device via USB
2. During setup, choose "USB Connection"
3. Optionally specify the device serial number

### Bluetooth Connection (Linux only)
1. Ensure your device is paired with the system
2. Install bluepy successfully (see solutions above)
3. During setup, choose "Bluetooth Connection"
4. Enter the Bluetooth MAC address

## Error Messages and Solutions

### "Bluetooth support not available"
- **Solution**: Install bluepy using one of the methods above
- **Alternative**: Use USB connection only

### "Failed to connect to Radiacode device"
- **Check**: Device is connected and powered on
- **Check**: USB drivers are installed (Windows)
- **Check**: Device permissions (Linux)

### "Invalid MAC address format"
- **Format**: Use `XX:XX:XX:XX:XX:XX` or `XX-XX-XX-XX-XX-XX`
- **Example**: `52:43:01:02:03:04`

## Getting Help

If you continue to have issues:

1. **Check the logs**: Look for detailed error messages in Home Assistant logs
2. **Try USB first**: USB connection is more reliable and doesn't require bluepy
3. **Verify device**: Ensure your Radiacode device is working with the official software
4. **Check permissions**: Ensure your user has access to USB/Bluetooth devices

## Alternative: Use USB Only

If you're having trouble with Bluetooth setup, you can use USB connection which is:
- ✅ **More reliable**
- ✅ **No build tools required**
- ✅ **Works on all platforms**
- ✅ **Faster data transfer**

Simply choose "USB Connection" during setup and connect your device via USB cable.