# Radiacode Home Assistant Integration - Installation Guide

This guide explains how to install and configure the Radiacode Home Assistant integration for monitoring radiation detectors and spectrometers.

## Prerequisites

- Home Assistant 2023.8 or later
- Radiacode device (RadiaCode-10x or compatible)
- USB cable or Bluetooth capability (Linux only for Bluetooth)
- For USB support: `usb` library (PyUSB)
- For Bluetooth support: `bluepy` library (Linux only)

## Installation Methods

### Method 1: Manual Installation (Recommended)

1. **Download the Integration**
   ```bash
   # Clone or download the integration files
   # Copy the custom_components/radiacode folder to your Home Assistant config directory
   ```

2. **Install Dependencies** (if needed)
   ```bash
   # For USB support (usually already available in Home Assistant)
   pip install usb
   
   # For Bluetooth support on Linux
   pip install bluepy
   ```

3. **Restart Home Assistant**
   - Go to **Settings** → **System** → **Restart**
   - Or restart your Home Assistant instance

4. **Add the Integration**
   - Go to **Settings** → **Devices & Services** → **Integrations**
   - Click **+ Add Integration**
   - Search for "Radiacode"
   - Follow the setup wizard

### Method 2: HACS Installation

1. **Install HACS** (if not already installed)
   - Follow the [HACS installation guide](https://hacs.xyz/docs/installation/installation/)

2. **Add Custom Repository**
   - Go to **HACS** → **Integrations** → **Custom Repositories**
   - Add this repository URL
   - Set category to "Integration"

3. **Install the Integration**
   - Find "Radiacode" in HACS
   - Click **Download**
   - Restart Home Assistant

4. **Configure the Integration**
   - Follow the same steps as Method 1, step 4

## Configuration

### USB Connection

1. **Connect Device**
   - Connect your Radiacode device via USB
   - Ensure the device is powered on

2. **Setup Process**
   - Choose "USB Connection" during setup
   - Optionally specify the device serial number if you have multiple devices
   - The integration will automatically detect and connect to the device

### Bluetooth Connection (Linux Only)

1. **Pair Device**
   - Ensure your Radiacode device is paired with your Home Assistant system
   - Note the Bluetooth MAC address of your device

2. **Setup Process**
   - Choose "Bluetooth Connection" during setup
   - Enter the Bluetooth MAC address (e.g., `52:43:01:02:03:04`)
   - The integration will connect to the device via Bluetooth

## Available Entities

### Sensors

| Entity | Description | Unit |
|--------|-------------|------|
| `sensor.radiacode_count_rate` | Real-time radiation count rate | cps |
| `sensor.radiacode_dose_rate` | Radiation dose rate | μSv/h |
| `sensor.radiacode_temperature` | Device temperature | °C |
| `sensor.radiacode_battery` | Battery charge level | % |
| `sensor.radiacode_accumulated_dose` | Total accumulated dose | μSv |
| `sensor.radiacode_spectrum_duration` | Spectrum measurement duration | s |
| `sensor.radiacode_spectrum_total_counts` | Total spectrum counts | counts |

### Binary Sensors

| Entity | Description |
|--------|-------------|
| `binary_sensor.radiacode_alarm_1` | Alarm 1 threshold exceeded |
| `binary_sensor.radiacode_alarm_2` | Alarm 2 threshold exceeded |
| `binary_sensor.radiacode_device_on` | Device power status |

### Switches

| Entity | Description |
|--------|-------------|
| `switch.radiacode_device_power` | Control device power |
| `switch.radiacode_sound` | Control sound alerts |
| `switch.radiacode_vibration` | Control vibration alerts |
| `switch.radiacode_display` | Control display on/off |

## Services

The integration provides several custom services for advanced control:

### `radiacode.reset_dose`
Reset the accumulated dose counter.

### `radiacode.reset_spectrum`
Reset the spectrum data.

### `radiacode.set_display_brightness`
Set display brightness (0-9).

**Parameters:**
- `brightness` (int): Brightness level from 0 (off) to 9 (maximum)

### `radiacode.get_spectrum`
Get current spectrum data.

### `radiacode.get_energy_calibration`
Get energy calibration coefficients.

### `radiacode.set_energy_calibration`
Set energy calibration coefficients.

**Parameters:**
- `a0` (float): Constant term coefficient (keV)
- `a1` (float): Linear term coefficient (keV/channel)
- `a2` (float): Quadratic term coefficient (keV/channel²)

## Automation Examples

### High Radiation Alert

```yaml
automation:
  - alias: "High Radiation Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.radiacode_dose_rate
      above: 10  # 10 μSv/h
    action:
      - service: notify.mobile_app
        data:
          title: "High Radiation Alert"
          message: "Dose rate is {{ states('sensor.radiacode_dose_rate') }} μSv/h"
```

### Daily Dose Reset

```yaml
automation:
  - alias: "Daily Dose Reset"
    trigger:
      platform: time
      at: "00:00:00"
    action:
      - service: radiacode.reset_dose
```

### Spectrum Data Collection

```yaml
automation:
  - alias: "Collect Spectrum Data"
    trigger:
      platform: time_pattern
      hours: "/6"  # Every 6 hours
    action:
      - service: radiacode.get_spectrum
```

## Troubleshooting

### Connection Issues

**USB Connection Fails:**
- Ensure the device is properly connected and powered on
- Check USB permissions (may need udev rules on Linux)
- Try specifying the serial number during setup
- Verify the device works with official Radiacode software

**Bluetooth Connection Fails:**
- Verify the MAC address is correct
- Ensure the device is paired and discoverable
- Check Bluetooth permissions on your system
- Note: Bluetooth is only supported on Linux

### Data Not Updating

1. Check the integration status in **Settings** → **Devices & Services**
2. Verify the device is connected and powered on
3. Check the Home Assistant logs for error messages
4. Restart the integration if needed

### Platform-Specific Notes

#### Linux
- ✅ Full support for both USB and Bluetooth connections
- 📝 May need udev rules for USB access without root
- 📝 Install required Bluetooth libraries: `sudo apt-get install libbluetooth-dev`

#### macOS
- ✅ USB connectivity works out of the box
- ❌ Bluetooth is not supported (bluepy limitation)
- 📝 Install libusb: `brew install libusb`

#### Windows
- ✅ USB connectivity supported
- ❌ Bluetooth is not supported (bluepy limitation)
- 📝 May need USB drivers

## Support

For issues and feature requests:

1. Check the [Home Assistant logs](https://www.home-assistant.io/integrations/logger/) for error messages
2. Verify your device is working with the official Radiacode software
3. Report issues with detailed logs and device information

## License

This integration is licensed under the MIT License, same as the underlying Radiacode Python library.