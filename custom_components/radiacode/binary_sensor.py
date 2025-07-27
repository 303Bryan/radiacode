"""Support for Radiacode binary sensors."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_BLUETOOTH_MAC,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    BINARY_SENSOR_ALARM_1,
    BINARY_SENSOR_ALARM_2,
    BINARY_SENSOR_DEVICE_ON,
)
from .coordinator import RadiacodeCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Radiacode binary sensors based on a config entry."""
    coordinator: RadiacodeCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        RadiacodeAlarm1BinarySensor(coordinator, config_entry),
        RadiacodeAlarm2BinarySensor(coordinator, config_entry),
        RadiacodeDeviceOnBinarySensor(coordinator, config_entry),
    ]

    async_add_entities(entities)


class RadiacodeBaseBinarySensor(BinarySensorEntity):
    """Base class for Radiacode binary sensors."""

    def __init__(
        self,
        coordinator: RadiacodeCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
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


class RadiacodeAlarm1BinarySensor(RadiacodeBaseBinarySensor):
    """Representation of a Radiacode alarm 1 binary sensor."""

    _attr_name = "Alarm 1"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        if not self.coordinator.data or not self.coordinator.data.get("alarms"):
            return False
        return self.coordinator.data["alarms"]["alarm_1"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or not self.coordinator.data.get("real_time_data"):
            return {}
        
        data = self.coordinator.data["real_time_data"]
        return {
            "count_rate": data.get("count_rate"),
            "dose_rate": data.get("dose_rate"),
            "timestamp": data.get("timestamp").isoformat() if data.get("timestamp") else None,
        }


class RadiacodeAlarm2BinarySensor(RadiacodeBaseBinarySensor):
    """Representation of a Radiacode alarm 2 binary sensor."""

    _attr_name = "Alarm 2"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        if not self.coordinator.data or not self.coordinator.data.get("alarms"):
            return False
        return self.coordinator.data["alarms"]["alarm_2"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or not self.coordinator.data.get("real_time_data"):
            return {}
        
        data = self.coordinator.data["real_time_data"]
        return {
            "count_rate": data.get("count_rate"),
            "dose_rate": data.get("dose_rate"),
            "timestamp": data.get("timestamp").isoformat() if data.get("timestamp") else None,
        }


class RadiacodeDeviceOnBinarySensor(RadiacodeBaseBinarySensor):
    """Representation of a Radiacode device on binary sensor."""

    _attr_name = "Device On"
    _attr_device_class = BinarySensorDeviceClass.POWER

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        if not self.coordinator.data or not self.coordinator.data.get("device_status"):
            return True  # Default to on if no data
        return self.coordinator.data["device_status"]["device_on"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data or not self.coordinator.data.get("device_status"):
            return {}
        
        data = self.coordinator.data["device_status"]
        return {
            "sound_on": data.get("sound_on"),
            "vibration_on": data.get("vibration_on"),
            "display_on": data.get("display_on"),
        }