# Radiacode Home Assistant Integration

This integration provides Home Assistant support for [Radiacode](https://www.radiacode.com/) radiation detectors and spectrometers. It allows you to monitor real-time radiation measurements, spectrum data, and control device settings directly from Home Assistant.

## Features

- **Real-time Radiation Monitoring**: Track count rate and dose rate measurements
- **Device Status Monitoring**: Monitor temperature, battery level, and accumulated dose
- **Spectrum Analysis**: Access energy spectrum data and calibration coefficients
- **Device Control**: Control device power, sound, vibration, and display settings
- **Alarm Monitoring**: Monitor device alarms and alerts
- **Bluetooth Support**: Connect via Bluetooth (Linux only) or USB
- **Custom Services**: Reset dose/spectrum, adjust display brightness, and manage calibration

## Installation

### Method 1: Manual Installation (Recommended)

1. Download this integration folder to your Home Assistant `config/custom_components/radiacode/` directory
2. Restart Home Assistant
3. Go to **Settings** → **Devices & Services** → **Integrations**
4. Click **+ Add Integration** and search for "Radiacode"
5. Follow the setup wizard

### Method 2: HACS Installation

1. Install [HACS](https://hacs.xyz/) if you haven't already
2. Add this repository as a custom repository in HACS
3. Install the integration through HACS
4. Restart Home Assistant and follow the setup wizard

## Configuration

### USB Connection

1. Connect your Radiacode device via USB
2. During setup, choose "USB Connection"
3. Optionally specify the device serial number if you have multiple devices

### Bluetooth Connection (Linux Only)

1. Ensure your Radiacode device is paired with your Home Assistant system
2. During setup, choose "Bluetooth Connection"
3. Enter the Bluetooth MAC address of your device (e.g., `52:43:01:02:03:04`)

## Entities

### Sensors

- **Count Rate**: Real-time radiation count rate in counts per second (cps)
- **Dose Rate**: Radiation dose rate in microsieverts per hour (μSv/h)
- **Temperature**: Device temperature in Celsius
- **Battery**: Battery charge level as percentage
- **Accumulated Dose**: Total accumulated radiation dose in microsieverts (μSv)
- **Spectrum Duration**: Current spectrum measurement duration in seconds
- **Spectrum Total Counts**: Total counts in the current spectrum

### Binary Sensors

- **Alarm 1**: Indicates if Alarm 1 threshold is exceeded
- **Alarm 2**: Indicates if Alarm 2 threshold is exceeded
- **Device On**: Shows device power status

### Switches

- **Device Power**: Control device power on/off
- **Sound**: Control device sound alerts
- **Vibration**: Control device vibration alerts
- **Display**: Control display on/off (via brightness)

## Services

The integration provides several custom services for advanced control:

### `radiacode.reset_dose`
Reset the accumulated dose counter on the Radiacode device.

### `radiacode.reset_spectrum`
Reset the spectrum data on the Radiacode device.

### `radiacode.set_display_brightness`
Set the display brightness level (0-9) on the Radiacode device.

**Parameters:**
- `brightness` (int): Display brightness level from 0 (off) to 9 (maximum)

### `radiacode.get_spectrum`
Get current spectrum data from the Radiacode device.

### `radiacode.get_energy_calibration`
Get energy calibration coefficients from the Radiacode device.

### `radiacode.set_energy_calibration`
Set energy calibration coefficients on the Radiacode device.

**Parameters:**
- `a0` (float): Constant term coefficient (keV)
- `a1` (float): Linear term coefficient (keV/channel)
- `a2` (float): Quadratic term coefficient (keV/channel²)

## Automation Examples

### Monitor High Radiation Levels

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

### Reset Dose Counter Daily

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

1. **USB Connection Fails**:
   - Ensure the device is properly connected
   - Check USB permissions (may need udev rules on Linux)
   - Try specifying the serial number during setup

2. **Bluetooth Connection Fails**:
   - Verify the MAC address is correct
   - Ensure the device is paired and discoverable
   - Check Bluetooth permissions on your system

### Data Not Updating

1. Check the integration status in **Settings** → **Devices & Services**
2. Verify the device is connected and powered on
3. Check the Home Assistant logs for error messages

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

## Requirements

- Home Assistant 2023.8 or later
- Python `radiacode` library version 0.2.0 or later
- USB or Bluetooth connection to Radiacode device

## Support

For issues and feature requests, please:

1. Check the [Home Assistant logs](https://www.home-assistant.io/integrations/logger/) for error messages
2. Verify your device is working with the official Radiacode software
3. Report issues with detailed logs and device information

## License

This integration is licensed under the MIT License, same as the underlying Radiacode Python library.