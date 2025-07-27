"""Config flow for the Radiacode integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_BLUETOOTH_MAC,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    MANUFACTURER,
    MODEL,
)

_LOGGER = logging.getLogger(__name__)


class RadiacodeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Radiacode."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._bluetooth_mac: str | None = None
        self._serial_number: str | None = None
        self._name: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            self._name = user_input[CONF_NAME]
            return await self.async_step_connection_type()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default="Radiacode"): str,
                }
            ),
        )

    async def async_step_connection_type(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the connection type step."""
        if user_input is not None:
            connection_type = user_input["connection_type"]
            
            if connection_type == "bluetooth":
                return await self.async_step_bluetooth()
            else:
                return await self.async_step_usb()

        return self.async_show_form(
            step_id="connection_type",
            data_schema=vol.Schema(
                {
                    vol.Required("connection_type"): vol.In(
                        {
                            "usb": "USB Connection",
                            "bluetooth": "Bluetooth Connection",
                        }
                    ),
                }
            ),
        )

    async def async_step_bluetooth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the Bluetooth configuration step."""
        errors = {}

        if user_input is not None:
            bluetooth_mac = user_input[CONF_BLUETOOTH_MAC].upper()
            
            # Validate MAC address format
            if not self._is_valid_mac(bluetooth_mac):
                errors["base"] = "invalid_mac"
            else:
                self._bluetooth_mac = bluetooth_mac
                
                # Test connection
                try:
                    from .radiacode_lib import RadiaCode
                    device = RadiaCode(bluetooth_mac=bluetooth_mac)
                    device_info = {
                        "serial_number": device.serial_number(),
                        "firmware_version": device.fw_version(),
                    }
                    
                    return self.async_create_entry(
                        title=self._name,
                        data={
                            CONF_NAME: self._name,
                            CONF_BLUETOOTH_MAC: bluetooth_mac,
                        },
                        description_placeholders={
                            "device_info": f"SN: {device_info['serial_number']}, FW: {device_info['firmware_version']}"
                        },
                    )
                except Exception as ex:
                    _LOGGER.error("Failed to connect to Radiacode device: %s", ex)
                    errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="bluetooth",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_BLUETOOTH_MAC,
                        description="Enter the Bluetooth MAC address of your Radiacode device (e.g., 52:43:01:02:03:04)"
                    ): str,
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
                from .radiacode_lib import RadiaCode
                device = RadiaCode(serial_number=serial_number)
                device_info = {
                    "serial_number": device.serial_number(),
                    "firmware_version": device.fw_version(),
                }
                
                return self.async_create_entry(
                    title=self._name,
                    data={
                        CONF_NAME: self._name,
                        CONF_SERIAL_NUMBER: serial_number,
                    },
                    description_placeholders={
                        "device_info": f"SN: {device_info['serial_number']}, FW: {device_info['firmware_version']}"
                    },
                )
            except Exception as ex:
                _LOGGER.error("Failed to connect to Radiacode device: %s", ex)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="usb",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SERIAL_NUMBER,
                        description="Enter the serial number of your Radiacode device (optional, will use first available device if not specified)"
                    ): str,
                }
            ),
            errors=errors,
        )

    def _is_valid_mac(self, mac: str) -> bool:
        """Validate MAC address format."""
        import re
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        return bool(mac_pattern.match(mac))

    async def async_step_import(self, import_info: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_info)