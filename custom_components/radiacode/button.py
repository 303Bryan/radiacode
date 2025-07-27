"""Button platform for RadiaCode integration."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import RadiaCodeDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up RadiaCode buttons based on a config entry."""
    coordinator: RadiaCodeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[ButtonEntity] = [
        RadiaCodeResetDoseButton(coordinator, entry),
        RadiaCodeResetSpectrumButton(coordinator, entry),
    ]

    async_add_entities(entities)


class RadiaCodeButtonEntity(CoordinatorEntity, ButtonEntity):
    """Base class for RadiaCode buttons."""

    def __init__(
        self,
        coordinator: RadiaCodeDataUpdateCoordinator,
        entry: ConfigEntry,
        button_type: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.entry = entry
        self.button_type = button_type
        self._attr_has_entity_name = True
        
        # Set unique ID
        device_serial = entry.data.get("serial_number", "unknown")
        self._attr_unique_id = f"{device_serial}_{button_type}"
        
        # Set device info
        self._attr_device_info = coordinator.device_info

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.device is not None


class RadiaCodeResetDoseButton(RadiaCodeButtonEntity):
    """Button to reset accumulated dose."""

    def __init__(
        self,
        coordinator: RadiaCodeDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the reset dose button."""
        super().__init__(coordinator, entry, "reset_dose")
        self._attr_name = "Reset dose"
        self._attr_icon = "mdi:refresh"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.hass.async_add_executor_job(
                self.coordinator.device.dose_reset
            )
            _LOGGER.info("RadiaCode dose reset successfully")
            # Request an immediate update
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to reset RadiaCode dose: %s", err)


class RadiaCodeResetSpectrumButton(RadiaCodeButtonEntity):
    """Button to reset spectrum data."""

    def __init__(
        self,
        coordinator: RadiaCodeDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the reset spectrum button."""
        super().__init__(coordinator, entry, "reset_spectrum")
        self._attr_name = "Reset spectrum"
        self._attr_icon = "mdi:chart-histogram"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.hass.async_add_executor_job(
                self.coordinator.device.spectrum_reset
            )
            _LOGGER.info("RadiaCode spectrum reset successfully")
            # Request an immediate update
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to reset RadiaCode spectrum: %s", err)