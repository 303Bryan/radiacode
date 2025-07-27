"""RadiaCode Integration for Home Assistant.

This integration provides support for RadiaCode radiation detectors,
allowing real-time monitoring of radiation levels, spectrum analysis,
and device configuration through Home Assistant.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_BLUETOOTH_MAC,
    CONF_SERIAL_NUMBER,
    CONF_UPDATE_INTERVAL,
    CONF_SPECTRUM_ENABLED,
    DEFAULT_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SELECT,
    Platform.NUMBER,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up RadiaCode from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = RadiaCodeDataUpdateCoordinator(hass, entry)
    
    # Test connection
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class RadiaCodeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the RadiaCode device."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.entry = entry
        self._device = None
        self._device_info = None
        
        # Get configuration
        self.bluetooth_mac = entry.data.get(CONF_BLUETOOTH_MAC)
        self.serial_number = entry.data.get(CONF_SERIAL_NUMBER)
        self.spectrum_enabled = entry.options.get(CONF_SPECTRUM_ENABLED, True)
        
        update_interval = timedelta(
            seconds=entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_setup_device(self) -> None:
        """Set up the RadiaCode device connection."""
        if self._device is not None:
            return

        try:
            # Import RadiaCode here to avoid blocking the event loop during startup
            from radiacode import RadiaCode
            
            # Create device connection based on configuration
            if self.bluetooth_mac:
                self._device = await self.hass.async_add_executor_job(
                    RadiaCode, None, None, True  # bluetooth_mac, serial_number, ignore_firmware_check
                )
                # Note: Due to bluepy limitations, we'll need to handle Bluetooth differently
                # For now, we'll fall back to USB connection
                _LOGGER.warning(
                    "Bluetooth connection requested but may not be supported through proxies. "
                    "Consider using USB connection for reliable operation."
                )
            else:
                self._device = await self.hass.async_add_executor_job(
                    RadiaCode, None, self.serial_number, True
                )

            # Get device information
            fw_version = await self.hass.async_add_executor_job(
                self._device.fw_version
            )
            device_name = await self.hass.async_add_executor_job(
                self._device.device_name
            )
            serial = await self.hass.async_add_executor_job(
                self._device.serial_number
            )

            self._device_info = DeviceInfo(
                identifiers={(DOMAIN, serial)},
                name=f"RadiaCode {device_name}",
                manufacturer="RadiaCode",
                model=device_name,
                sw_version=f"{fw_version[1][0]}.{fw_version[1][1]}.{fw_version[1][2]}",
                serial_number=serial,
            )

            _LOGGER.info(
                "Connected to RadiaCode device: %s (Serial: %s, FW: %s)",
                device_name,
                serial,
                f"{fw_version[1][0]}.{fw_version[1][1]}.{fw_version[1][2]}",
            )

        except Exception as err:
            _LOGGER.error("Failed to connect to RadiaCode device: %s", err)
            raise UpdateFailed(f"Failed to connect to RadiaCode device: {err}") from err

    async def _async_update_data(self) -> dict:
        """Update data via library."""
        if self._device is None:
            await self._async_setup_device()

        try:
            # Get real-time data
            data_buf = await self.hass.async_add_executor_job(
                self._device.data_buf
            )
            
            # Process the data buffer for the latest measurements
            latest_data = None
            for record in data_buf:
                from radiacode.types import RealTimeData
                if isinstance(record, RealTimeData):
                    latest_data = record
                    break

            if latest_data is None:
                raise UpdateFailed("No real-time data available")

            # Get device status
            battery_level = None
            try:
                # Try to get battery level if available
                battery_level = await self.hass.async_add_executor_job(
                    self._device.battery_level
                )
            except AttributeError:
                # Battery level might not be available on all firmware versions
                pass

            # Get energy calibration coefficients
            energy_calib = await self.hass.async_add_executor_job(
                self._device.energy_calib
            )

            data = {
                "dose_rate": latest_data.dose_rate,
                "dose_rate_error": latest_data.dose_rate_err,
                "count_rate": latest_data.count_rate,
                "count_rate_error": latest_data.count_rate_err,
                "flags": latest_data.flags,
                "real_time_flags": latest_data.real_time_flags,
                "timestamp": latest_data.dt,
                "battery_level": battery_level,
                "energy_calibration": energy_calib,
            }

            # Get spectrum data if enabled
            if self.spectrum_enabled:
                try:
                    spectrum = await self.hass.async_add_executor_job(
                        self._device.spectrum
                    )
                    data["spectrum"] = {
                        "duration": spectrum.duration,
                        "counts": spectrum.counts,
                        "channels": len(spectrum.counts),
                        "total_counts": sum(spectrum.counts),
                    }
                except Exception as err:
                    _LOGGER.debug("Failed to get spectrum data: %s", err)

            return data

        except Exception as err:
            _LOGGER.error("Error fetching RadiaCode data: %s", err)
            raise UpdateFailed(f"Error fetching RadiaCode data: {err}") from err

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device information."""
        return self._device_info

    @property
    def device(self):
        """Return the RadiaCode device instance."""
        return self._device