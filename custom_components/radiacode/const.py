"""Constants for the Radiacode integration."""
from typing import Final

DOMAIN: Final = "radiacode"

# Configuration keys
CONF_BLUETOOTH_MAC: Final = "bluetooth_mac"
CONF_SERIAL_NUMBER: Final = "serial_number"

# Platforms
PLATFORMS: Final = ["sensor", "binary_sensor", "switch"]

# Device info
MANUFACTURER: Final = "Radiacode"
MODEL: Final = "RadiaCode-10x"

# Sensor types
SENSOR_COUNT_RATE: Final = "count_rate"
SENSOR_DOSE_RATE: Final = "dose_rate"
SENSOR_TEMPERATURE: Final = "temperature"
SENSOR_BATTERY: Final = "battery"
SENSOR_ACCUMULATED_DOSE: Final = "accumulated_dose"
SENSOR_SPECTRUM_DURATION: Final = "spectrum_duration"
SENSOR_SPECTRUM_TOTAL_COUNTS: Final = "spectrum_total_counts"

# Binary sensor types
BINARY_SENSOR_ALARM_1: Final = "alarm_1"
BINARY_SENSOR_ALARM_2: Final = "alarm_2"
BINARY_SENSOR_DEVICE_ON: Final = "device_on"

# Switch types
SWITCH_DEVICE_POWER: Final = "device_power"
SWITCH_SOUND: Final = "sound"
SWITCH_VIBRATION: Final = "vibration"
SWITCH_DISPLAY: Final = "display"

# Update intervals
UPDATE_INTERVAL: Final = 10  # seconds
SPECTRUM_UPDATE_INTERVAL: Final = 60  # seconds

# Units
UNIT_COUNT_RATE: Final = "cps"  # counts per second
UNIT_DOSE_RATE: Final = "μSv/h"  # microsieverts per hour
UNIT_DOSE: Final = "μSv"  # microsieverts
UNIT_TEMPERATURE: Final = "°C"
UNIT_BATTERY: Final = "%"
UNIT_DURATION: Final = "s"  # seconds