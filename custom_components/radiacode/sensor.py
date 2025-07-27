"""Support for Radiacode sensors."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import (
    CONF_BLUETOOTH_MAC,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    SENSOR_ACCUMULATED_DOSE,
    SENSOR_BATTERY,
    SENSOR_COUNT_RATE,
    SENSOR_DOSE_RATE,
    SENSOR_SPECTRUM_DURATION,
    SENSOR_SPECTRUM_TOTAL_COUNTS,
    SENSOR_TEMPERATURE,
    UNIT_COUNT_RATE,
    UNIT_DOSE,
    UNIT_DOSE_RATE,
    UNIT_DURATION,
)
from .coordinator import RadiacodeCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Radiacode sensors based on a config entry."""
    coordinator: RadiacodeCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        RadiacodeCountRateSensor(coordinator, config_entry),
        RadiacodeDoseRateSensor(coordinator, config_entry),
        RadiacodeTemperatureSensor(coordinator, config_entry),
        RadiacodeBatterySensor(coordinator, config_entry),
        RadiacodeAccumulatedDoseSensor(coordinator, config_entry),
        RadiacodeSpectrumDurationSensor(coordinator, config_entry),
        RadiacodeSpectrumTotalCountsSensor(coordinator, config_entry),
    ]

    async_add_entities(entities)


class RadiacodeBaseSensor(SensorEntity):
    """Base class for Radiacode sensors."""

    def __init__(
        self,
        coordinator: RadiacodeCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.config_entry = config_entry
        self._attr_has_entity_name = True
        self._attr_should_poll = False

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.config_entry.entry_id)},
            name=self.config_entry.data[CONF_NAME],
            manufacturer=MANUFACTURER,
            model=MODEL,
            serial_number=self.config_entry.data.get(CONF_SERIAL_NUMBER),
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success


class RadiacodeCountRateSensor(RadiacodeBaseSensor):
    """Representation of a Radiacode count rate sensor."""

    _attr_name = "Count Rate"
    _attr_native_unit_of_measurement = UNIT_COUNT_RATE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.FREQUENCY

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.get("real_time_data"):
            return None
        return self.coordinator.data["real_time_data"]["count_rate"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or not self.coordinator.data.get("real_time_data"):
            return {}
        
        data = self.coordinator.data["real_time_data"]
        return {
            "count_rate_error": data.get("count_rate_error"),
            "timestamp": data.get("timestamp").isoformat() if data.get("timestamp") else None,
        }


class RadiacodeDoseRateSensor(RadiacodeBaseSensor):
    """Representation of a Radiacode dose rate sensor."""

    _attr_name = "Dose Rate"
    _attr_native_unit_of_measurement = UNIT_DOSE_RATE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.get("real_time_data"):
            return None
        return self.coordinator.data["real_time_data"]["dose_rate"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or not self.coordinator.data.get("real_time_data"):
            return {}
        
        data = self.coordinator.data["real_time_data"]
        return {
            "dose_rate_error": data.get("dose_rate_error"),
            "timestamp": data.get("timestamp").isoformat() if data.get("timestamp") else None,
        }


class RadiacodeTemperatureSensor(RadiacodeBaseSensor):
    """Representation of a Radiacode temperature sensor."""

    _attr_name = "Temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.TEMPERATURE

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.get("rare_data"):
            return None
        return self.coordinator.data["rare_data"]["temperature"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or not self.coordinator.data.get("rare_data"):
            return {}
        
        data = self.coordinator.data["rare_data"]
        return {
            "duration": data.get("duration"),
            "timestamp": data.get("timestamp").isoformat() if data.get("timestamp") else None,
        }


class RadiacodeBatterySensor(RadiacodeBaseSensor):
    """Representation of a Radiacode battery sensor."""

    _attr_name = "Battery"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.BATTERY

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.get("rare_data"):
            return None
        return self.coordinator.data["rare_data"]["charge_level"]


class RadiacodeAccumulatedDoseSensor(RadiacodeBaseSensor):
    """Representation of a Radiacode accumulated dose sensor."""

    _attr_name = "Accumulated Dose"
    _attr_native_unit_of_measurement = UNIT_DOSE
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.get("rare_data"):
            return None
        return self.coordinator.data["rare_data"]["dose"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or not self.coordinator.data.get("rare_data"):
            return {}
        
        data = self.coordinator.data["rare_data"]
        return {
            "duration": data.get("duration"),
            "timestamp": data.get("timestamp").isoformat() if data.get("timestamp") else None,
        }


class RadiacodeSpectrumDurationSensor(RadiacodeBaseSensor):
    """Representation of a Radiacode spectrum duration sensor."""

    _attr_name = "Spectrum Duration"
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.get("spectrum"):
            return None
        return self.coordinator.data["spectrum"]["duration"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or not self.coordinator.data.get("spectrum"):
            return {}
        
        data = self.coordinator.data["spectrum"]
        return {
            "total_counts": data.get("total_counts"),
            "calibration_a0": data.get("calibration", {}).get("a0"),
            "calibration_a1": data.get("calibration", {}).get("a1"),
            "calibration_a2": data.get("calibration", {}).get("a2"),
            "timestamp": data.get("timestamp").isoformat() if data.get("timestamp") else None,
        }


class RadiacodeSpectrumTotalCountsSensor(RadiacodeBaseSensor):
    """Representation of a Radiacode spectrum total counts sensor."""

    _attr_name = "Spectrum Total Counts"
    _attr_native_unit_of_measurement = "counts"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.get("spectrum"):
            return None
        return self.coordinator.data["spectrum"]["total_counts"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or not self.coordinator.data.get("spectrum"):
            return {}
        
        data = self.coordinator.data["spectrum"]
        return {
            "duration": data.get("duration"),
            "calibration_a0": data.get("calibration", {}).get("a0"),
            "calibration_a1": data.get("calibration", {}).get("a1"),
            "calibration_a2": data.get("calibration", {}).get("a2"),
            "timestamp": data.get("timestamp").isoformat() if data.get("timestamp") else None,
        }