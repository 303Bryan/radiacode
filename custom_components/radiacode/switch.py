"""Support for Radiacode switches."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    SWITCH_DEVICE_POWER,
    SWITCH_SOUND,
    SWITCH_VIBRATION,
    SWITCH_DISPLAY,
)
from .coordinator import RadiacodeCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Radiacode switches based on a config entry."""
    coordinator: RadiacodeCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        RadiacodeDevicePowerSwitch(coordinator, config_entry),
        RadiacodeSoundSwitch(coordinator, config_entry),
        RadiacodeVibrationSwitch(coordinator, config_entry),
        RadiacodeDisplaySwitch(coordinator, config_entry),
    ]

    async_add_entities(entities)


class RadiacodeBaseSwitch(SwitchEntity):
    """Base class for Radiacode switches."""

    def __init__(
        self,
        coordinator: RadiacodeCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the switch."""
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


class RadiacodeDevicePowerSwitch(RadiacodeBaseSwitch):
    """Representation of a Radiacode device power switch."""

    _attr_name = "Device Power"

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        if not self.coordinator.data or not self.coordinator.data.get("device_status"):
            return True  # Default to on if no data
        return self.coordinator.data["device_status"]["device_on"]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        await self.coordinator.async_set_device_power(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        await self.coordinator.async_set_device_power(False)


class RadiacodeSoundSwitch(RadiacodeBaseSwitch):
    """Representation of a Radiacode sound switch."""

    _attr_name = "Sound"

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        if not self.coordinator.data or not self.coordinator.data.get("device_status"):
            return False  # Default to off if no data
        return self.coordinator.data["device_status"]["sound_on"]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the sound on."""
        await self.coordinator.async_set_sound(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the sound off."""
        await self.coordinator.async_set_sound(False)


class RadiacodeVibrationSwitch(RadiacodeBaseSwitch):
    """Representation of a Radiacode vibration switch."""

    _attr_name = "Vibration"

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        if not self.coordinator.data or not self.coordinator.data.get("device_status"):
            return False  # Default to off if no data
        return self.coordinator.data["device_status"]["vibration_on"]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the vibration on."""
        await self.coordinator.async_set_vibration(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the vibration off."""
        await self.coordinator.async_set_vibration(False)


class RadiacodeDisplaySwitch(RadiacodeBaseSwitch):
    """Representation of a Radiacode display switch."""

    _attr_name = "Display"

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        if not self.coordinator.data or not self.coordinator.data.get("device_status"):
            return True  # Default to on if no data
        return self.coordinator.data["device_status"]["display_on"]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the display on."""
        # Set brightness to a reasonable level (5 out of 9)
        await self.coordinator.async_set_display_brightness(5)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the display off."""
        # Set brightness to 0 to turn off display
        await self.coordinator.async_set_display_brightness(0)