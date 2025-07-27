# RadiaCode Home Assistant Integration

A comprehensive Home Assistant custom component for [RadiaCode radiation detectors](https://www.radiacode.com/), providing real-time radiation monitoring, spectrum analysis, and device configuration through your Home Assistant dashboard.

## Features

### 📊 Real-time Monitoring
- **Dose Rate**: Continuous radiation dose rate monitoring in µSv/h
- **Count Rate**: Radiation count rate in counts per second (CPS)
- **Measurement Errors**: Real-time error calculations and confidence intervals
- **Device Status**: Connection status and battery level monitoring

### 📈 Spectrum Analysis
- **Total Counts**: Total spectrum counts collection
- **Duration Tracking**: Spectrum collection time monitoring
- **Energy Calibration**: Access to device energy calibration coefficients
- **Histogram Data**: Full spectrum data for analysis and visualization

### 🔧 Device Configuration
- **Display Settings**: Brightness control (0-9 levels) and auto-off timing
- **Audio/Vibration**: Sound and vibration notification controls
- **Language**: Support for English and Russian interface languages
- **Reset Functions**: Reset accumulated dose and spectrum data

### 🔗 Connectivity Options
- **USB Connection**: Direct USB connection support for all platforms
- **Bluetooth Proxy**: Integration with ESPHome Bluetooth proxies for remote monitoring
- **Auto-Discovery**: Automatic device detection and configuration

## Installation

### Prerequisites

1. **Home Assistant** version 2023.1 or later
2. **RadiaCode device** with firmware version 4.8 or later
3. **ESPHome Bluetooth Proxy** (for Bluetooth connectivity) - optional

### Method 1: Manual Installation

1. **Download the Integration**
   ```bash
   cd /config/custom_components
   git clone https://github.com/your-repo/radiacode.git
   ```

2. **Install Dependencies**
   The integration will automatically install the required `radiacode` Python library.

3. **Restart Home Assistant**
   ```bash
   # Restart Home Assistant to load the new integration
   ```

### Method 2: HACS Installation (Recommended)

1. **Add Custom Repository**
   - Open HACS in Home Assistant
   - Go to "Integrations" 
   - Click the three dots menu → "Custom repositories"
   - Add repository URL: `https://github.com/your-repo/radiacode`
   - Category: "Integration"

2. **Install Integration**
   - Search for "RadiaCode" in HACS
   - Click "Download"
   - Restart Home Assistant

## Configuration

### Adding a RadiaCode Device

1. **Navigate to Integrations**
   - Go to **Settings** → **Devices & Services**
   - Click **"+ Add Integration"**
   - Search for **"RadiaCode"**

2. **Device Setup**
   - **Device Name**: Enter a friendly name for your device
   - **Connection Method**: Choose between USB or Bluetooth
     - **USB**: Leave Bluetooth MAC empty for USB connection
     - **Bluetooth**: Enter device MAC address (requires Bluetooth proxy)
   - **Serial Number**: Optional - specify for multiple USB devices

3. **Configuration Options**
   - **Update Interval**: How often to poll device (10-300 seconds, default: 30)
   - **Spectrum Enabled**: Enable/disable spectrum data collection

### Bluetooth Proxy Setup

For wireless monitoring using Bluetooth proxies:

1. **Install ESPHome Bluetooth Proxy**
   ```yaml
   # ESPHome configuration example
   esphome:
     name: radiacode-proxy
   
   esp32:
     board: esp32dev
     framework:
       type: esp-idf
   
   wifi:
     ssid: "your-wifi"
     password: "your-password"
   
   api:
   ota:
   logger:
   
   esp32_ble_tracker:
     scan_parameters:
       active: true
   
   bluetooth_proxy:
     active: true
   ```

2. **Find Device MAC Address**
   - Use ESPHome logs or a Bluetooth scanner app
   - Look for device named "Radon" or similar
   - Note the 17-character MAC address (e.g., `52:43:01:02:03:04`)

## Entities

The integration creates the following entities for each RadiaCode device:

### Sensors
- `sensor.radiacode_dose_rate` - Current radiation dose rate (µSv/h)
- `sensor.radiacode_count_rate` - Current count rate (CPS)
- `sensor.radiacode_spectrum_total_counts` - Total spectrum counts
- `sensor.radiacode_spectrum_duration` - Spectrum collection time
- `sensor.radiacode_battery_level` - Device battery level (%)

### Binary Sensors
- `binary_sensor.radiacode_device_connected` - Device connectivity status

### Controls
- `button.radiacode_reset_dose` - Reset accumulated dose
- `button.radiacode_reset_spectrum` - Reset spectrum data
- `select.radiacode_language` - Device language selection
- `number.radiacode_display_brightness` - Display brightness (0-9)
- `number.radiacode_display_off_time` - Auto-off time (seconds)

### Attributes

Each sensor includes detailed attributes:

**Dose Rate Sensor:**
- `dose_rate_error` - Measurement error percentage
- `flags` - Device status flags
- `real_time_flags` - Real-time status flags
- `energy_calibration` - Energy calibration coefficients
- `last_measurement` - Timestamp of last measurement

**Spectrum Sensors:**
- `spectrum_channels` - Number of spectrum channels
- `collection_duration` - Data collection time

## Services

The integration provides several services for device control:

### `radiacode.reset_dose`
Reset accumulated radiation dose measurement.

### `radiacode.reset_spectrum`
Reset spectrum data collection.

### `radiacode.set_display_brightness`
Set display brightness level.
```yaml
service: radiacode.set_display_brightness
target:
  device_id: your_radiacode_device
data:
  brightness: 7  # 0-9
```

### `radiacode.set_sound`
Enable/disable sound notifications.
```yaml
service: radiacode.set_sound
target:
  device_id: your_radiacode_device
data:
  enabled: true
```

### `radiacode.set_vibration`
Enable/disable vibration notifications.
```yaml
service: radiacode.set_vibration
target:
  device_id: your_radiacode_device
data:
  enabled: false
```

### `radiacode.set_language`
Set device display language.
```yaml
service: radiacode.set_language
target:
  device_id: your_radiacode_device
data:
  language: "en"  # "en" or "ru"
```

## Automation Examples

### Radiation Alert
```yaml
automation:
  - alias: "High Radiation Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.radiacode_dose_rate
      above: 1.0  # µSv/h
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ High Radiation Detected"
          message: "Dose rate: {{ states('sensor.radiacode_dose_rate') }} µSv/h"
      - service: light.turn_on
        target:
          entity_id: light.warning_light
        data:
          color_name: red
          flash: long
```

### Daily Dose Report
```yaml
automation:
  - alias: "Daily Radiation Report"
    trigger:
      platform: time
      at: "23:59:00"
    action:
      - service: notify.persistent_notification
        data:
          title: "Daily Radiation Summary"
          message: >
            Today's radiation levels:
            Current: {{ states('sensor.radiacode_dose_rate') }} µSv/h
            Total counts: {{ states('sensor.radiacode_spectrum_total_counts') }}
            Collection time: {{ states('sensor.radiacode_spectrum_duration') }}s
```

### Device Connection Monitoring
```yaml
automation:
  - alias: "RadiaCode Disconnected"
    trigger:
      platform: state
      entity_id: binary_sensor.radiacode_device_connected
      to: 'off'
      for:
        minutes: 5
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "📡 RadiaCode Disconnected"
          message: "Check USB connection or Bluetooth proxy"
```

## Dashboard Cards

### Basic Radiation Monitor
```yaml
type: entities
title: Radiation Monitor
entities:
  - sensor.radiacode_dose_rate
  - sensor.radiacode_count_rate
  - binary_sensor.radiacode_device_connected
  - sensor.radiacode_battery_level
```

### Spectrum Analysis Card
```yaml
type: glance
title: Spectrum Analysis
entities:
  - sensor.radiacode_spectrum_total_counts
  - sensor.radiacode_spectrum_duration
columns: 2
```

### Device Controls
```yaml
type: entities
title: RadiaCode Controls
entities:
  - button.radiacode_reset_dose
  - button.radiacode_reset_spectrum
  - select.radiacode_language
  - number.radiacode_display_brightness
```

## Troubleshooting

### Connection Issues

**USB Connection Problems:**
- Ensure device is powered on and connected
- Check USB cable and port
- Verify device drivers are installed
- Try different USB port

**Bluetooth Connection Problems:**
- Ensure Bluetooth proxy is running and in range
- Verify MAC address is correct
- Check proxy logs for connection attempts
- Restart Bluetooth proxy if needed

### Performance Issues

**Slow Updates:**
- Increase update interval in integration options
- Disable spectrum collection if not needed
- Check system resources and logs

**High CPU Usage:**
- Reduce update frequency
- Consider using USB instead of Bluetooth
- Check for other high-resource integrations

### Data Issues

**Missing Data:**
- Check device connectivity
- Verify firmware compatibility (≥4.8)
- Review integration logs for errors
- Try restarting the integration

## Platform Support

### Operating Systems
- **Linux**: ✅ Full USB and Bluetooth support
- **Windows**: ✅ USB support, ❌ Bluetooth limitations  
- **macOS**: ✅ USB support, ❌ Bluetooth not supported

### Home Assistant
- **Core**: ✅ Supported
- **Supervised**: ✅ Supported
- **Container**: ✅ Supported
- **OS**: ✅ Supported

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/radiacode/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/radiacode/discussions)
- **Documentation**: [RadiaCode Library](https://github.com/cdump/radiacode)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [RadiaCode Library](https://github.com/cdump/radiacode) by cdump
- [RadiaCode Hardware](https://www.radiacode.com/) by RadiaCode Ltd.
- Home Assistant community for integration development support