"""Config flow for RadiaCode integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_BLUETOOTH_MAC,
    CONF_SERIAL_NUMBER,
    CONF_UPDATE_INTERVAL,
    CONF_SPECTRUM_ENABLED,
    CONF_DEVICE_NAME,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_NAME,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Optional(CONF_BLUETOOTH_MAC): cv.string,
        vol.Optional(CONF_SERIAL_NUMBER): cv.string,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    try:
        from radiacode import RadiaCode
        
        # Try to connect to the device
        bluetooth_mac = data.get(CONF_BLUETOOTH_MAC)
        serial_number = data.get(CONF_SERIAL_NUMBER)
        
        if not bluetooth_mac and not serial_number:
            # Try to connect to any available device
            device = await hass.async_add_executor_job(
                RadiaCode, None, None, True
            )
        elif bluetooth_mac:
            device = await hass.async_add_executor_job(
                RadiaCode, bluetooth_mac, None, True
            )
        else:
            device = await hass.async_add_executor_job(
                RadiaCode, None, serial_number, True
            )

        # Get device information
        device_name = await hass.async_add_executor_job(device.device_name)
        serial = await hass.async_add_executor_job(device.serial_number)
        fw_version = await hass.async_add_executor_job(device.fw_version)

        return {
            "title": f"RadiaCode {device_name}",
            "device_name": device_name,
            "serial_number": serial,
            "firmware_version": f"{fw_version[1][0]}.{fw_version[1][1]}.{fw_version[1][2]}",
        }

    except Exception as err:
        _LOGGER.error("Failed to connect to RadiaCode device: %s", err)
        raise CannotConnect from err


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for RadiaCode."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            # Create a unique ID based on the device serial number
            await self.async_set_unique_id(info["serial_number"])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=info["title"],
                data={
                    CONF_NAME: user_input.get(CONF_NAME, DEFAULT_NAME),
                    CONF_BLUETOOTH_MAC: user_input.get(CONF_BLUETOOTH_MAC),
                    CONF_SERIAL_NUMBER: user_input.get(CONF_SERIAL_NUMBER),
                    CONF_DEVICE_NAME: info["device_name"],
                    "firmware_version": info["firmware_version"],
                    "serial_number": info["serial_number"],
                },
                options={
                    CONF_UPDATE_INTERVAL: DEFAULT_UPDATE_INTERVAL,
                    CONF_SPECTRUM_ENABLED: True,
                },
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """RadiaCode config flow options handler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_UPDATE_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                    ),
                ): vol.All(int, vol.Range(min=10, max=300)),
                vol.Optional(
                    CONF_SPECTRUM_ENABLED,
                    default=self.config_entry.options.get(CONF_SPECTRUM_ENABLED, True),
                ): bool,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""