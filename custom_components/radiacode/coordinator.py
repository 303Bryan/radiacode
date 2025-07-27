"""Coordinator for the Radiacode integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from radiacode import RadiaCode, RealTimeData, RareData, Spectrum

from .const import (
    UPDATE_INTERVAL,
    SPECTRUM_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class RadiacodeCoordinator(DataUpdateCoordinator):
    """Coordinator for Radiacode device data."""

    def __init__(
        self,
        hass: HomeAssistant,
        bluetooth_mac: str | None,
        serial_number: str | None,
        name: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        
        self._bluetooth_mac = bluetooth_mac
        self._serial_number = serial_number
        self._device: RadiaCode | None = None
        self._last_spectrum_update = datetime.now()
        self._spectrum_data: dict[str, Any] = {}
        
    async def async_connect(self) -> None:
        """Connect to the Radiacode device."""
        try:
            if self._bluetooth_mac:
                _LOGGER.info("Connecting to Radiacode device via Bluetooth: %s", self._bluetooth_mac)
                self._device = RadiaCode(bluetooth_mac=self._bluetooth_mac)
            else:
                _LOGGER.info("Connecting to Radiacode device via USB")
                self._device = RadiaCode(serial_number=self._serial_number)
                
            # Test connection by getting device info
            device_info = {
                "serial_number": self._device.serial_number(),
                "firmware_version": self._device.fw_version(),
                "hardware_serial": self._device.hw_serial_number(),
            }
            _LOGGER.info("Connected to Radiacode device: %s", device_info)
            
        except Exception as ex:
            _LOGGER.error("Failed to connect to Radiacode device: %s", ex)
            raise

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        if self._device:
            # Note: RadiaCode library doesn't have explicit disconnect method
            self._device = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data from the Radiacode device."""
        if not self._device:
            await self.async_connect()
            
        try:
            data: dict[str, Any] = {
                "last_update": datetime.now(),
                "real_time_data": None,
                "rare_data": None,
                "alarms": {
                    "alarm_1": False,
                    "alarm_2": False,
                },
                "device_status": {
                    "device_on": True,
                    "sound_on": False,
                    "vibration_on": False,
                    "display_on": True,
                },
            }
            
            # Get real-time data
            databuf = self._device.data_buf()
            latest_real_time = None
            latest_rare = None
            
            for record in databuf:
                if isinstance(record, RealTimeData):
                    latest_real_time = record
                elif isinstance(record, RareData):
                    latest_rare = record
                    
            if latest_real_time:
                data["real_time_data"] = {
                    "count_rate": latest_real_time.count_rate,
                    "count_rate_error": latest_real_time.count_rate_err,
                    "dose_rate": latest_real_time.dose_rate,
                    "dose_rate_error": latest_real_time.dose_rate_err,
                    "timestamp": latest_real_time.dt,
                    "flags": latest_real_time.flags,
                }
                
            if latest_rare:
                data["rare_data"] = {
                    "duration": latest_rare.duration,
                    "dose": latest_rare.dose,
                    "temperature": latest_rare.temperature,
                    "charge_level": latest_rare.charge_level,
                    "flags": latest_rare.flags,
                }
                
            # Update spectrum data periodically
            now = datetime.now()
            if (now - self._last_spectrum_update).total_seconds() >= SPECTRUM_UPDATE_INTERVAL:
                try:
                    spectrum = self._device.spectrum()
                    data["spectrum"] = {
                        "duration": spectrum.duration.total_seconds(),
                        "total_counts": sum(spectrum.counts),
                        "calibration": {
                            "a0": spectrum.a0,
                            "a1": spectrum.a1,
                            "a2": spectrum.a2,
                        },
                        "counts": spectrum.counts,
                        "timestamp": now,
                    }
                    self._last_spectrum_update = now
                except Exception as ex:
                    _LOGGER.warning("Failed to update spectrum data: %s", ex)
                    
            # Get device configuration
            try:
                # These might fail if device doesn't support them
                data["device_status"]["sound_on"] = self._device.get_sound_on()
                data["device_status"]["vibration_on"] = self._device.get_vibro_on()
            except:
                pass  # Not all devices support these queries
                
            return data
            
        except Exception as ex:
            _LOGGER.error("Error updating Radiacode data: %s", ex)
            raise UpdateFailed(f"Error updating Radiacode data: {ex}") from ex

    async def async_set_device_power(self, power_on: bool) -> None:
        """Set device power state."""
        if not self._device:
            raise RuntimeError("Device not connected")
            
        self._device.set_device_on(power_on)
        await self.async_request_refresh()

    async def async_set_sound(self, sound_on: bool) -> None:
        """Set device sound state."""
        if not self._device:
            raise RuntimeError("Device not connected")
            
        self._device.set_sound_on(sound_on)
        await self.async_request_refresh()

    async def async_set_vibration(self, vibration_on: bool) -> None:
        """Set device vibration state."""
        if not self._device:
            raise RuntimeError("Device not connected")
            
        self._device.set_vibro_on(vibration_on)
        await self.async_request_refresh()

    async def async_set_display_brightness(self, brightness: int) -> None:
        """Set display brightness (0-9)."""
        if not self._device:
            raise RuntimeError("Device not connected")
            
        self._device.set_display_brightness(brightness)
        await self.async_request_refresh()

    async def async_reset_dose(self) -> None:
        """Reset accumulated dose."""
        if not self._device:
            raise RuntimeError("Device not connected")
            
        self._device.dose_reset()
        await self.async_request_refresh()

    async def async_reset_spectrum(self) -> None:
        """Reset spectrum data."""
        if not self._device:
            raise RuntimeError("Device not connected")
            
        self._device.spectrum_reset()
        await self.async_request_refresh()

    async def async_get_spectrum(self) -> dict[str, Any]:
        """Get current spectrum data."""
        if not self._device:
            raise RuntimeError("Device not connected")
            
        spectrum = self._device.spectrum()
        return {
            "duration": spectrum.duration.total_seconds(),
            "total_counts": sum(spectrum.counts),
            "calibration": {
                "a0": spectrum.a0,
                "a1": spectrum.a1,
                "a2": spectrum.a2,
            },
            "counts": spectrum.counts,
            "timestamp": datetime.now(),
        }

    async def async_get_energy_calibration(self) -> list[float]:
        """Get energy calibration coefficients."""
        if not self._device:
            raise RuntimeError("Device not connected")
            
        return self._device.energy_calib()

    async def async_set_energy_calibration(self, coefficients: list[float]) -> None:
        """Set energy calibration coefficients."""
        if not self._device:
            raise RuntimeError("Device not connected")
            
        self._device.set_energy_calib(coefficients)
        await self.async_request_refresh()