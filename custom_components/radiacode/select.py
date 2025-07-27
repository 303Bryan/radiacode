"""Select platform for RadiaCode integration."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
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
    """Set up RadiaCode select entities based on a config entry."""
    coordinator: RadiaCodeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SelectEntity] = [
        RadiaCodeLanguageSelect(coordinator, entry),
    ]

    async_add_entities(entities)


class RadiaCodeSelectEntity(CoordinatorEntity, SelectEntity):
    """Base class for RadiaCode select entities."""

    def __init__(
        self,
        coordinator: RadiaCodeDataUpdateCoordinator,
        entry: ConfigEntry,
        select_type: str,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.entry = entry
        self.select_type = select_type
        self._attr_has_entity_name = True
        
        # Set unique ID
        device_serial = entry.data.get("serial_number", "unknown")
        self._attr_unique_id = f"{device_serial}_{select_type}"
        
        # Set device info
        self._attr_device_info = coordinator.device_info

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.device is not None


class RadiaCodeLanguageSelect(RadiaCodeSelectEntity):
    """Select entity for device language."""

    def __init__(
        self,
        coordinator: RadiaCodeDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the language select."""
        super().__init__(coordinator, entry, "language")
        self._attr_name = "Language"
        self._attr_icon = "mdi:translate"
        self._attr_options = ["en", "ru"]
        self._current_language = None

    @property
    def current_option(self) -> str | None:
        """Return the current selected language."""
        # We'll need to track this since RadiaCode doesn't provide a way to read current language
        return self._current_language

    async def async_select_option(self, option: str) -> None:
        """Change the selected language."""
        try:
            await self.hass.async_add_executor_job(
                self.coordinator.device.set_language, option
            )
            self._current_language = option
            _LOGGER.info("RadiaCode language set to: %s", option)
            # Request an immediate update
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set RadiaCode language: %s", err)