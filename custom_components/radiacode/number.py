"""Number platform for RadiaCode integration."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import RadiaCodeDataUpdateCoordinator
from .const import (
    DOMAIN,
    CONF_BRIGHTNESS_MIN,
    CONF_BRIGHTNESS_MAX,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up RadiaCode number entities based on a config entry."""
    coordinator: RadiaCodeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[NumberEntity] = [
        RadiaCodeDisplayBrightnessNumber(coordinator, entry),
        RadiaCodeDisplayOffTimeNumber(coordinator, entry),
    ]

    async_add_entities(entities)


class RadiaCodeNumberEntity(CoordinatorEntity, NumberEntity):
    """Base class for RadiaCode number entities."""

    def __init__(
        self,
        coordinator: RadiaCodeDataUpdateCoordinator,
        entry: ConfigEntry,
        number_type: str,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self.entry = entry
        self.number_type = number_type
        self._attr_has_entity_name = True
        
        # Set unique ID
        device_serial = entry.data.get("serial_number", "unknown")
        self._attr_unique_id = f"{device_serial}_{number_type}"
        
        # Set device info
        self._attr_device_info = coordinator.device_info

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.device is not None


class RadiaCodeDisplayBrightnessNumber(RadiaCodeNumberEntity):
    """Number entity for display brightness control."""

    def __init__(
        self,
        coordinator: RadiaCodeDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the display brightness number."""
        super().__init__(coordinator, entry, "display_brightness")
        self._attr_name = "Display brightness"
        self._attr_icon = "mdi:brightness-6"
        self._attr_native_min_value = CONF_BRIGHTNESS_MIN
        self._attr_native_max_value = CONF_BRIGHTNESS_MAX
        self._attr_native_step = 1
        self._attr_mode = NumberMode.SLIDER
        self._current_brightness = 5  # Default value

    @property
    def native_value(self) -> float:
        """Return the current brightness value."""
        return self._current_brightness

    async def async_set_native_value(self, value: float) -> None:
        """Set the brightness value."""
        try:
            brightness = int(value)
            await self.hass.async_add_executor_job(
                self.coordinator.device.set_display_brightness, brightness
            )
            self._current_brightness = brightness
            _LOGGER.info("RadiaCode display brightness set to: %d", brightness)
            # Request an immediate update
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set RadiaCode display brightness: %s", err)


class RadiaCodeDisplayOffTimeNumber(RadiaCodeNumberEntity):
    """Number entity for display auto-off time control."""

    def __init__(
        self,
        coordinator: RadiaCodeDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the display off time number."""
        super().__init__(coordinator, entry, "display_off_time")
        self._attr_name = "Display off time"
        self._attr_icon = "mdi:timer-off"
        self._attr_native_min_value = 5
        self._attr_native_max_value = 300
        self._attr_native_step = 5
        self._attr_native_unit_of_measurement = "s"
        self._attr_mode = NumberMode.BOX
        self._current_off_time = 30  # Default value

    @property
    def native_value(self) -> float:
        """Return the current display off time value."""
        return self._current_off_time

    async def async_set_native_value(self, value: float) -> None:
        """Set the display off time value."""
        try:
            off_time = int(value)
            await self.hass.async_add_executor_job(
                self.coordinator.device.set_display_off_time, off_time
            )
            self._current_off_time = off_time
            _LOGGER.info("RadiaCode display off time set to: %d seconds", off_time)
            # Request an immediate update
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set RadiaCode display off time: %s", err)