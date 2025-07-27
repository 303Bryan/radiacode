"""Constants for the RadiaCode integration."""
from __future__ import annotations

from homeassistant.const import (
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfTime,
)

# Integration domain
DOMAIN = "radiacode"

# Configuration keys
CONF_BLUETOOTH_MAC = "bluetooth_mac"
CONF_SERIAL_NUMBER = "serial_number"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_SPECTRUM_ENABLED = "spectrum_enabled"
CONF_DEVICE_NAME = "device_name"

# Default values
DEFAULT_UPDATE_INTERVAL = 30  # seconds
DEFAULT_NAME = "RadiaCode"

# Radiation units
UNIT_DOSE_RATE_USV_H = "µSv/h"
UNIT_DOSE_RATE_MR_H = "mR/h"
UNIT_COUNT_RATE_CPS = "CPS"
UNIT_COUNT_RATE_CPM = "CPM"
UNIT_DOSE_USV = "µSv"
UNIT_DOSE_MR = "mR"

# Device classes for sensors
DEVICE_CLASS_RADIATION = "radiation"

# Entity names
ENTITY_DOSE_RATE = "dose_rate"
ENTITY_COUNT_RATE = "count_rate"
ENTITY_SPECTRUM_TOTAL_COUNTS = "spectrum_total_counts"
ENTITY_SPECTRUM_DURATION = "spectrum_duration"
ENTITY_BATTERY_LEVEL = "battery_level"
ENTITY_DEVICE_CONNECTED = "device_connected"

# Attributes
ATTR_DOSE_RATE_ERROR = "dose_rate_error"
ATTR_COUNT_RATE_ERROR = "count_rate_error"
ATTR_FLAGS = "flags"
ATTR_REAL_TIME_FLAGS = "real_time_flags"
ATTR_ENERGY_CALIBRATION = "energy_calibration"
ATTR_SPECTRUM_CHANNELS = "spectrum_channels"
ATTR_FIRMWARE_VERSION = "firmware_version"
ATTR_SERIAL_NUMBER = "serial_number"

# Service names
SERVICE_RESET_DOSE = "reset_dose"
SERVICE_RESET_SPECTRUM = "reset_spectrum"
SERVICE_SET_DISPLAY_BRIGHTNESS = "set_display_brightness"
SERVICE_SET_SOUND = "set_sound"
SERVICE_SET_VIBRATION = "set_vibration"

# Configuration options
CONF_BRIGHTNESS_MIN = 0
CONF_BRIGHTNESS_MAX = 9