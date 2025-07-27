"""Sensor platform for RadiaCode integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import RadiaCodeDataUpdateCoordinator
from .const import (
    DOMAIN,
    ENTITY_DOSE_RATE,
    ENTITY_COUNT_RATE,
    ENTITY_SPECTRUM_TOTAL_COUNTS,
    ENTITY_SPECTRUM_DURATION,
    ENTITY_BATTERY_LEVEL,
    UNIT_DOSE_RATE_USV_H,
    UNIT_COUNT_RATE_CPS,
    ATTR_DOSE_RATE_ERROR,
    ATTR_COUNT_RATE_ERROR,
    ATTR_FLAGS,
    ATTR_REAL_TIME_FLAGS,
    ATTR_ENERGY_CALIBRATION,
    ATTR_SPECTRUM_CHANNELS,
    DEVICE_CLASS_RADIATION,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up RadiaCode sensors based on a config entry."""
    coordinator: RadiaCodeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        RadiaCodeDoseRateSensor(coordinator, entry),
        RadiaCodeCountRateSensor(coordinator, entry),
    ]

    # Add spectrum sensors if spectrum data is enabled
    if coordinator.spectrum_enabled:
        entities.extend([
            RadiaCodeSpectrumTotalCountsSensor(coordinator, entry),
            RadiaCodeSpectrumDurationSensor(coordinator, entry),
        ])

    # Add battery sensor if available
    if coordinator.data and coordinator.data.get("battery_level") is not None:
        entities.append(RadiaCodeBatterySensor(coordinator, entry))

    async_add_entities(entities)


class RadiaCodeSensorEntity(CoordinatorEntity, SensorEntity):
    """Base class for RadiaCode sensors."""

    def __init__(
        self,
        coordinator: RadiaCodeDataUpdateCoordinator,
        entry: ConfigEntry,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self.sensor_type = sensor_type
        self._attr_has_entity_name = True
        
        # Set unique ID
        device_serial = entry.data.get("serial_number", "unknown")
        self._attr_unique_id = f"{device_serial}_{sensor_type}"
        
        # Set device info
        self._attr_device_info = coordinator.device_info

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None


class RadiaCodeDoseRateSensor(RadiaCodeSensorEntity):
    """Sensor for radiation dose rate."""

    def __init__(
        self,
        coordinator: RadiaCodeDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the dose rate sensor."""
        super().__init__(coordinator, entry, ENTITY_DOSE_RATE)
        self._attr_name = "Dose rate"
        self._attr_native_unit_of_measurement = UNIT_DOSE_RATE_USV_H
        self._attr_device_class = DEVICE_CLASS_RADIATION
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:radioactive"

    @property
    def native_value(self) -> float | None:
        """Return the dose rate value."""
        if self.coordinator.data:
            return self.coordinator.data.get("dose_rate")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return None

        attrs = {}
        
        if error := self.coordinator.data.get("dose_rate_error"):
            attrs[ATTR_DOSE_RATE_ERROR] = f"{error:.1f}%"
        
        if flags := self.coordinator.data.get("flags"):
            attrs[ATTR_FLAGS] = flags
            
        if rt_flags := self.coordinator.data.get("real_time_flags"):
            attrs[ATTR_REAL_TIME_FLAGS] = rt_flags
            
        if energy_calib := self.coordinator.data.get("energy_calibration"):
            attrs[ATTR_ENERGY_CALIBRATION] = energy_calib
            
        if timestamp := self.coordinator.data.get("timestamp"):
            attrs["last_measurement"] = timestamp.isoformat()

        return attrs


class RadiaCodeCountRateSensor(RadiaCodeSensorEntity):
    """Sensor for radiation count rate."""

    def __init__(
        self,
        coordinator: RadiaCodeDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the count rate sensor."""
        super().__init__(coordinator, entry, ENTITY_COUNT_RATE)
        self._attr_name = "Count rate"
        self._attr_native_unit_of_measurement = UNIT_COUNT_RATE_CPS
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:counter"

    @property
    def native_value(self) -> float | None:
        """Return the count rate value."""
        if self.coordinator.data:
            return self.coordinator.data.get("count_rate")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return None

        attrs = {}
        
        if error := self.coordinator.data.get("count_rate_error"):
            attrs[ATTR_COUNT_RATE_ERROR] = f"{error:.1f}%"
            
        if timestamp := self.coordinator.data.get("timestamp"):
            attrs["last_measurement"] = timestamp.isoformat()

        return attrs


class RadiaCodeSpectrumTotalCountsSensor(RadiaCodeSensorEntity):
    """Sensor for spectrum total counts."""

    def __init__(
        self,
        coordinator: RadiaCodeDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the spectrum total counts sensor."""
        super().__init__(coordinator, entry, ENTITY_SPECTRUM_TOTAL_COUNTS)
        self._attr_name = "Spectrum total counts"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_icon = "mdi:chart-histogram"

    @property
    def native_value(self) -> int | None:
        """Return the spectrum total counts."""
        if self.coordinator.data and "spectrum" in self.coordinator.data:
            return self.coordinator.data["spectrum"].get("total_counts")
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            super().available
            and self.coordinator.data
            and "spectrum" in self.coordinator.data
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if not self.coordinator.data or "spectrum" not in self.coordinator.data:
            return None

        spectrum_data = self.coordinator.data["spectrum"]
        attrs = {}
        
        if channels := spectrum_data.get("channels"):
            attrs[ATTR_SPECTRUM_CHANNELS] = channels
            
        if duration := spectrum_data.get("duration"):
            attrs["collection_duration"] = f"{duration} seconds"

        return attrs


class RadiaCodeSpectrumDurationSensor(RadiaCodeSensorEntity):
    """Sensor for spectrum collection duration."""

    def __init__(
        self,
        coordinator: RadiaCodeDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the spectrum duration sensor."""
        super().__init__(coordinator, entry, ENTITY_SPECTRUM_DURATION)
        self._attr_name = "Spectrum duration"
        self._attr_native_unit_of_measurement = UnitOfTime.SECONDS
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:timer"

    @property
    def native_value(self) -> float | None:
        """Return the spectrum collection duration."""
        if self.coordinator.data and "spectrum" in self.coordinator.data:
            return self.coordinator.data["spectrum"].get("duration")
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            super().available
            and self.coordinator.data
            and "spectrum" in self.coordinator.data
        )


class RadiaCodeBatterySensor(RadiaCodeSensorEntity):
    """Sensor for battery level."""

    def __init__(
        self,
        coordinator: RadiaCodeDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the battery sensor."""
        super().__init__(coordinator, entry, ENTITY_BATTERY_LEVEL)
        self._attr_name = "Battery level"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_device_class = SensorDeviceClass.BATTERY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:battery"

    @property
    def native_value(self) -> int | None:
        """Return the battery level."""
        if self.coordinator.data:
            return self.coordinator.data.get("battery_level")
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            super().available
            and self.coordinator.data
            and self.coordinator.data.get("battery_level") is not None
        )