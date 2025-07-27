"""Binary sensor platform for RadiaCode integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import RadiaCodeDataUpdateCoordinator
from .const import (
    DOMAIN,
    ENTITY_DEVICE_CONNECTED,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up RadiaCode binary sensors based on a config entry."""
    coordinator: RadiaCodeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[BinarySensorEntity] = [
        RadiaCodeConnectivitySensor(coordinator, entry),
    ]

    async_add_entities(entities)


class RadiaCodeBinarySensorEntity(CoordinatorEntity, BinarySensorEntity):
    """Base class for RadiaCode binary sensors."""

    def __init__(
        self,
        coordinator: RadiaCodeDataUpdateCoordinator,
        entry: ConfigEntry,
        sensor_type: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self.sensor_type = sensor_type
        self._attr_has_entity_name = True
        
        # Set unique ID
        device_serial = entry.data.get("serial_number", "unknown")
        self._attr_unique_id = f"{device_serial}_{sensor_type}"
        
        # Set device info
        self._attr_device_info = coordinator.device_info


class RadiaCodeConnectivitySensor(RadiaCodeBinarySensorEntity):
    """Binary sensor for device connectivity status."""

    def __init__(
        self,
        coordinator: RadiaCodeDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the connectivity sensor."""
        super().__init__(coordinator, entry, ENTITY_DEVICE_CONNECTED)
        self._attr_name = "Device connected"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
        self._attr_icon = "mdi:usb"

    @property
    def is_on(self) -> bool:
        """Return true if device is connected."""
        return self.coordinator.last_update_success and self.coordinator.data is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return None

        attrs = {}
        
        if timestamp := self.coordinator.data.get("timestamp"):
            attrs["last_successful_update"] = timestamp.isoformat()
            
        # Connection method
        if self.coordinator.bluetooth_mac:
            attrs["connection_type"] = "Bluetooth"
            attrs["bluetooth_mac"] = self.coordinator.bluetooth_mac
        else:
            attrs["connection_type"] = "USB"
            if self.coordinator.serial_number:
                attrs["serial_number"] = self.coordinator.serial_number

        return attrs