"""Config flow for Radiacode integration."""
from __future__ import annotations

import logging
import re
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_BLUETOOTH_MAC, CONF_SERIAL_NUMBER, DOMAIN

_LOGGER = logging.getLogger(__name__)


class RadiacodeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Radiacode."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required("name"): str,
                    }
                ),
            )

        self._name = user_input["name"]
        return await self.async_step_connection_type()

    async def async_step_connection_type(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the connection type step."""
        if user_input is None:
            return self.async_show_form(
                step_id="connection_type",
                data_schema=vol.Schema(
                    {
                        vol.Required("connection_type"): vol.In(["usb", "bluetooth"]),
                    }
                ),
            )

        connection_type = user_input["connection_type"]
        if connection_type == "bluetooth":
            return await self.async_step_bluetooth()
        else:
            return await self.async_step_usb()

    async def async_step_bluetooth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the Bluetooth configuration step."""
        errors = {}

        if user_input is not None:
            bluetooth_mac = user_input[CONF_BLUETOOTH_MAC].upper()
            
            # Validate MAC address format
            if not self._is_valid_mac(bluetooth_mac):
                errors["base"] = "invalid_mac_address"
            else:
                # Test connection
                try:
                    from radiacode import RadiaCode
                    device = RadiaCode(bluetooth_mac=bluetooth_mac)
                    device_info = {
                        "serial_number": device.serial_number(),
                        "fw_version": device.fw_version(),
                    }
                    
                    # Create unique ID based on MAC address
                    unique_id = f"radiacode_{bluetooth_mac.replace(':', '')}"
                    
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()
                    
                    return self.async_create_entry(
                        title=self._name,
                        data={
                            CONF_BLUETOOTH_MAC: bluetooth_mac,
                            CONF_SERIAL_NUMBER: None,
                        },
                    )
                except ImportError:
                    errors["base"] = "bluetooth_not_supported"
                    _LOGGER.error("Bluetooth support not available. Install bluepy: pip install bluepy")
                except Exception as ex:
                    _LOGGER.error("Failed to connect to Radiacode device: %s", ex)
                    errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="bluetooth",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_BLUETOOTH_MAC): str,
                }
            ),
            errors=errors,
        )

    async def async_step_usb(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the USB configuration step."""
        errors = {}

        if user_input is not None:
            serial_number = user_input.get(CONF_SERIAL_NUMBER)
            
            try:
                from radiacode import RadiaCode
                device = RadiaCode(serial_number=serial_number)
                device_info = {
                    "serial_number": device.serial_number(),
                    "fw_version": device.fw_version(),
                }
                
                # Create unique ID based on serial number
                unique_id = f"radiacode_{device.serial_number()}"
                
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=self._name,
                    data={
                        CONF_BLUETOOTH_MAC: None,
                        CONF_SERIAL_NUMBER: serial_number,
                    },
                )
            except Exception as ex:
                _LOGGER.error("Failed to connect to Radiacode device: %s", ex)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="usb",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_SERIAL_NUMBER): str,
                }
            ),
            errors=errors,
        )

    def _is_valid_mac(self, mac: str) -> bool:
        """Validate MAC address format."""
        mac_pattern = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
        return bool(mac_pattern.match(mac))

    async def async_step_import(self, import_info: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_info)