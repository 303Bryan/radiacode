"""Services for the Radiacode integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SERVICE_RESET_DOSE = "reset_dose"
SERVICE_RESET_SPECTRUM = "reset_spectrum"
SERVICE_SET_DISPLAY_BRIGHTNESS = "set_display_brightness"
SERVICE_GET_SPECTRUM = "get_spectrum"
SERVICE_GET_ENERGY_CALIBRATION = "get_energy_calibration"
SERVICE_SET_ENERGY_CALIBRATION = "set_energy_calibration"

SERVICE_SCHEMA_RESET_DOSE = vol.Schema({})
SERVICE_SCHEMA_RESET_SPECTRUM = vol.Schema({})
SERVICE_SCHEMA_SET_DISPLAY_BRIGHTNESS = vol.Schema(
    {
        vol.Required("brightness"): vol.All(vol.Coerce(int), vol.Range(min=0, max=9))
    }
)
SERVICE_SCHEMA_GET_SPECTRUM = vol.Schema({})
SERVICE_SCHEMA_GET_ENERGY_CALIBRATION = vol.Schema({})
SERVICE_SCHEMA_SET_ENERGY_CALIBRATION = vol.Schema(
    {
        vol.Required("a0"): vol.Coerce(float),
        vol.Required("a1"): vol.Coerce(float),
        vol.Required("a2"): vol.Coerce(float),
    }
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the Radiacode integration."""

    async def async_reset_dose(call: ServiceCall) -> None:
        """Reset accumulated dose on the Radiacode device."""
        for entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry_id]
            try:
                await coordinator.async_reset_dose()
                _LOGGER.info("Reset accumulated dose for Radiacode device")
            except Exception as ex:
                _LOGGER.error("Failed to reset accumulated dose: %s", ex)

    async def async_reset_spectrum(call: ServiceCall) -> None:
        """Reset spectrum data on the Radiacode device."""
        for entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry_id]
            try:
                await coordinator.async_reset_spectrum()
                _LOGGER.info("Reset spectrum data for Radiacode device")
            except Exception as ex:
                _LOGGER.error("Failed to reset spectrum data: %s", ex)

    async def async_set_display_brightness(call: ServiceCall) -> None:
        """Set display brightness on the Radiacode device."""
        brightness = call.data["brightness"]
        for entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry_id]
            try:
                await coordinator.async_set_display_brightness(brightness)
                _LOGGER.info("Set display brightness to %d for Radiacode device", brightness)
            except Exception as ex:
                _LOGGER.error("Failed to set display brightness: %s", ex)

    async def async_get_spectrum(call: ServiceCall) -> None:
        """Get spectrum data from the Radiacode device."""
        for entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry_id]
            try:
                spectrum_data = await coordinator.async_get_spectrum()
                _LOGGER.info("Retrieved spectrum data: %s", spectrum_data)
                # You could store this in a sensor or return it via a response
            except Exception as ex:
                _LOGGER.error("Failed to get spectrum data: %s", ex)

    async def async_get_energy_calibration(call: ServiceCall) -> None:
        """Get energy calibration coefficients from the Radiacode device."""
        for entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry_id]
            try:
                calibration = await coordinator.async_get_energy_calibration()
                _LOGGER.info("Retrieved energy calibration: %s", calibration)
                # You could store this in a sensor or return it via a response
            except Exception as ex:
                _LOGGER.error("Failed to get energy calibration: %s", ex)

    async def async_set_energy_calibration(call: ServiceCall) -> None:
        """Set energy calibration coefficients on the Radiacode device."""
        a0 = call.data["a0"]
        a1 = call.data["a1"]
        a2 = call.data["a2"]
        
        for entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry_id]
            try:
                await coordinator.async_set_energy_calibration([a0, a1, a2])
                _LOGGER.info("Set energy calibration to [%f, %f, %f] for Radiacode device", a0, a1, a2)
            except Exception as ex:
                _LOGGER.error("Failed to set energy calibration: %s", ex)

    # Register services
    hass.services.async_register(
        DOMAIN,
        SERVICE_RESET_DOSE,
        async_reset_dose,
        schema=SERVICE_SCHEMA_RESET_DOSE,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_RESET_SPECTRUM,
        async_reset_spectrum,
        schema=SERVICE_SCHEMA_RESET_SPECTRUM,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_DISPLAY_BRIGHTNESS,
        async_set_display_brightness,
        schema=SERVICE_SCHEMA_SET_DISPLAY_BRIGHTNESS,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_SPECTRUM,
        async_get_spectrum,
        schema=SERVICE_SCHEMA_GET_SPECTRUM,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_ENERGY_CALIBRATION,
        async_get_energy_calibration,
        schema=SERVICE_SCHEMA_GET_ENERGY_CALIBRATION,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_ENERGY_CALIBRATION,
        async_set_energy_calibration,
        schema=SERVICE_SCHEMA_SET_ENERGY_CALIBRATION,
    )


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services for the Radiacode integration."""
    hass.services.async_remove(DOMAIN, SERVICE_RESET_DOSE)
    hass.services.async_remove(DOMAIN, SERVICE_RESET_SPECTRUM)
    hass.services.async_remove(DOMAIN, SERVICE_SET_DISPLAY_BRIGHTNESS)
    hass.services.async_remove(DOMAIN, SERVICE_GET_SPECTRUM)
    hass.services.async_remove(DOMAIN, SERVICE_GET_ENERGY_CALIBRATION)
    hass.services.async_remove(DOMAIN, SERVICE_SET_ENERGY_CALIBRATION)