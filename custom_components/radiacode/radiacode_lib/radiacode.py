"""Embedded RadiaCode Library for Home Assistant Integration

This module provides a self-contained Python interface for controlling RadiaCode 
radiation detection devices via USB or Bluetooth connections.
"""

import datetime
import platform
import struct
from typing import Optional, List, Union

from .bytes_buffer import BytesBuffer
from .decoders.databuf import decode_VS_DATA_BUF
from .decoders.spectrum import decode_RC_VS_SPECTRUM
from .transports.bluetooth import Bluetooth
from .transports.usb import Usb
from .types import (
    _VSFR_FORMATS,
    COMMAND,
    CTRL,
    VS,
    VSFR,
    AlarmLimits,
    DisplayDirection,
    DoseRateDB,
    Event,
    RareData,
    RawData,
    RealTimeData,
    Spectrum,
)


def spectrum_channel_to_energy(channel_number: int, a0: float, a1: float, a2: float) -> float:
    """Convert spectrometer channel number to energy in keV using quadratic calibration.

    Args:
        channel_number: Channel number from the spectrometer (integer)
        a0: Constant term coefficient (keV)
        a1: Linear term coefficient (keV/channel)
        a2: Quadratic term coefficient (keV/channel^2)

    Returns:
        float: Energy value in keV corresponding to the channel number
    """
    return a0 + a1 * channel_number + a2 * channel_number * channel_number


class RadiaCode:
    """Main RadiaCode device interface."""

    def __init__(
        self,
        bluetooth_mac: Optional[str] = None,
        serial_number: Optional[str] = None,
        ignore_firmware_compatibility_check: bool = False,
    ):
        """Initialize a RadiaCode device connection.

        This constructor establishes a connection to a RadiaCode device either via Bluetooth
        or USB, initializes the device, and performs firmware compatibility checks.

        Args:
            bluetooth_mac: Optional MAC address for Bluetooth connection. If provided and
                         Bluetooth is supported on the system, will connect via Bluetooth.
            serial_number: Optional USB serial number to connect to a specific device when
                         multiple devices are connected. Used only for USB connections.
            ignore_firmware_compatibility_check: If True, skips the firmware version
                                              compatibility check. Default is False.

        Raises:
            Exception: If the device firmware version is incompatible (< 4.8) and
                      ignore_firmware_compatibility_check is False.
        """
        self._seq = 0

        # Bluepy doesn't support MacOS: https://github.com/IanHarvey/bluepy/issues/44
        self._bt_supported = platform.system() != 'Darwin'

        if bluetooth_mac is not None and self._bt_supported is True:
            self._connection = Bluetooth(bluetooth_mac)
        else:
            self._connection = Usb(serial_number=serial_number)

        # init
        self.execute(COMMAND.SET_EXCHANGE, b'\x01\xff\x12\xff')
        self.set_local_time(datetime.datetime.now())
        self.device_time(0)
        self._base_time = datetime.datetime.now() + datetime.timedelta(seconds=128)

        (_, (vmaj, vmin, _)) = self.fw_version()
        if ignore_firmware_compatibility_check is False and vmaj < 4 or (vmaj == 4 and vmin < 8):
            raise Exception(
                f"Firmware version {vmaj}.{vmin} is not compatible. "
                "Please update to firmware version 4.8 or later."
            )

    def base_time(self) -> datetime.datetime:
        """Get the base time for the device."""
        return self._base_time

    def execute(self, reqtype: COMMAND, args: Optional[bytes] = None) -> BytesBuffer:
        """Execute a command on the device.

        Args:
            reqtype: The command type
            args: Optional command arguments

        Returns:
            BytesBuffer containing the response
        """
        self._seq = (self._seq + 1) % 256
        req = struct.pack('<BB', self._seq, int(reqtype))
        if args:
            req += args
        return self._connection.execute(req)

    def read_request(self, command_id: int | VS | VSFR) -> BytesBuffer:
        """Read data from the device.

        Args:
            command_id: The command ID to read

        Returns:
            BytesBuffer containing the response
        """
        return self.execute(COMMAND.RD_VIRT_SFR, struct.pack('<I', int(command_id)))

    def write_request(self, command_id: int | VSFR, data: Optional[bytes] = None) -> None:
        """Write data to the device.

        Args:
            command_id: The command ID to write
            data: Optional data to write
        """
        args = struct.pack('<I', int(command_id))
        if data:
            args += data
        self.execute(COMMAND.WR_VIRT_SFR, args)

    def batch_read_vsfrs(self, vsfr_ids: List[VSFR]) -> tuple[int | float]:
        """Read multiple VSFR values in a batch.

        Args:
            vsfr_ids: List of VSFR IDs to read

        Returns:
            Tuple of values read
        """
        args = struct.pack('<B', len(vsfr_ids))
        for vsfr_id in vsfr_ids:
            args += struct.pack('<I', int(vsfr_id))
        
        response = self.execute(COMMAND.RD_VIRT_SFR_BATCH, args)
        
        result = []
        for vsfr_id in vsfr_ids:
            if vsfr_id in _VSFR_FORMATS:
                fmt = _VSFR_FORMATS[vsfr_id]
                if fmt == "B":
                    result.append(response.read_uint8())
                elif fmt == "H":
                    result.append(response.read_uint16())
                elif fmt == "I":
                    result.append(response.read_uint32())
                elif fmt == "f":
                    result.append(response.read_float())
                else:
                    raise Exception(f"Unknown format {fmt} for VSFR {vsfr_id}")
            else:
                # Default to 32-bit integer for unknown VSFRs
                result.append(response.read_uint32())
        
        return tuple(result)

    def status(self) -> str:
        """Get device status.

        Returns:
            Device status string
        """
        response = self.execute(COMMAND.GET_STATUS)
        return response.read_string()

    def set_local_time(self, dt: datetime.datetime) -> None:
        """Set the local time on the device.

        Args:
            dt: The datetime to set
        """
        timestamp = int(dt.timestamp())
        self.execute(COMMAND.SET_TIME, struct.pack('<I', timestamp))

    def fw_signature(self) -> str:
        """Get firmware signature.

        Returns:
            Firmware signature string
        """
        response = self.execute(COMMAND.FW_SIGNATURE)
        return response.read_string()

    def fw_version(self) -> tuple[tuple[int, int, str], tuple[int, int, str]]:
        """Get firmware version information.

        Returns:
            Tuple of (boot_version, target_version) where each version is (major, minor, build)
        """
        response = self.execute(COMMAND.GET_VERSION)
        boot_major = response.read_uint8()
        boot_minor = response.read_uint8()
        boot_build = response.read_string()
        target_major = response.read_uint8()
        target_minor = response.read_uint8()
        target_build = response.read_string()
        
        return (
            (boot_major, boot_minor, boot_build),
            (target_major, target_minor, target_build)
        )

    def hw_serial_number(self) -> str:
        """Get hardware serial number.

        Returns:
            Hardware serial number string
        """
        response = self.execute(COMMAND.GET_SERIAL)
        return response.read_string()

    def configuration(self) -> str:
        """Get device configuration.

        Returns:
            Configuration string
        """
        response = self.read_request(VS.CONFIGURATION)
        return response.read_string()

    def text_message(self) -> str:
        """Get text message from device.

        Returns:
            Text message string
        """
        response = self.read_request(VS.TEXT_MESSAGE)
        return response.read_string()

    def serial_number(self) -> str:
        """Get device serial number.

        Returns:
            Serial number string
        """
        response = self.read_request(VS.SERIAL_NUMBER)
        return response.read_string()

    def commands(self) -> str:
        """Get available commands.

        Returns:
            Commands string
        """
        response = self.read_request(VS.FW_DESCRIPTOR)
        return response.read_string()

    def device_time(self, v: int) -> None:
        """Set device time.

        Args:
            v: Time value
        """
        self.write_request(VSFR.DEVICE_TIME, struct.pack('<I', v))

    def data_buf(self) -> List[Union[DoseRateDB, RareData, RealTimeData, RawData, Event]]:
        """Get data buffer from device.

        Returns:
            List of data records
        """
        response = self.read_request(VS.DATA_BUF)
        return decode_VS_DATA_BUF(response, self._base_time)

    def spectrum(self) -> Spectrum:
        """Get spectrum data from device.

        Returns:
            Spectrum object
        """
        response = self.read_request(VS.SPECTRUM)
        format_version = response.read_uint8()
        return decode_RC_VS_SPECTRUM(response, format_version)

    def spectrum_accum(self) -> Spectrum:
        """Get accumulated spectrum data from device.

        Returns:
            Spectrum object
        """
        response = self.read_request(VS.SPEC_ACCUM)
        format_version = response.read_uint8()
        return decode_RC_VS_SPECTRUM(response, format_version)

    def dose_reset(self) -> None:
        """Reset dose counter."""
        self.write_request(VSFR.DOSE_RESET, b'\x01')

    def spectrum_reset(self) -> None:
        """Reset spectrum data."""
        self.write_request(VSFR.SPEC_RESET, b'\x01')

    def energy_calib(self) -> List[float]:
        """Get energy calibration coefficients.

        Returns:
            List of calibration coefficients [a0, a1, a2]
        """
        response = self.read_request(VS.ENERGY_CALIB)
        a0 = response.read_float()
        a1 = response.read_float()
        a2 = response.read_float()
        return [a0, a1, a2]

    def set_energy_calib(self, coef: List[float]) -> None:
        """Set energy calibration coefficients.

        Args:
            coef: List of calibration coefficients [a0, a1, a2]
        """
        if len(coef) != 3:
            raise ValueError("Energy calibration must have exactly 3 coefficients")
        
        data = struct.pack('<fff', coef[0], coef[1], coef[2])
        self.write_request(VS.ENERGY_CALIB, data)

    def set_language(self, lang: str = 'ru') -> None:
        """Set device language.

        Args:
            lang: Language code ('en' or 'ru')
        """
        lang_code = 1 if lang == 'en' else 0
        self.write_request(VSFR.DEVICE_LANG, struct.pack('<B', lang_code))

    def set_device_on(self, on: bool) -> None:
        """Set device power state.

        Args:
            on: True to turn device on, False to turn off
        """
        self.write_request(VSFR.DEVICE_ON, struct.pack('<B', 1 if on else 0))

    def set_sound_on(self, on: bool) -> None:
        """Set device sound state.

        Args:
            on: True to enable sound, False to disable
        """
        self.write_request(VSFR.SOUND_ON, struct.pack('<B', 1 if on else 0))

    def set_vibro_on(self, on: bool) -> None:
        """Set device vibration state.

        Args:
            on: True to enable vibration, False to disable
        """
        self.write_request(VSFR.VIBRO_ON, struct.pack('<B', 1 if on else 0))

    def set_sound_ctrl(self, ctrls: List[CTRL]) -> None:
        """Set sound control flags.

        Args:
            ctrls: List of control flags
        """
        ctrl_value = sum(int(ctrl) for ctrl in ctrls)
        self.write_request(VSFR.SOUND_CTRL, struct.pack('<B', ctrl_value))

    def set_display_off_time(self, seconds: int) -> None:
        """Set display auto-off time.

        Args:
            seconds: Auto-off time in seconds
        """
        self.write_request(VSFR.DISP_OFF_TIME, struct.pack('<B', seconds))

    def set_display_brightness(self, brightness: int) -> None:
        """Set display brightness.

        Args:
            brightness: Brightness level (0-9)
        """
        if not 0 <= brightness <= 9:
            raise ValueError("Brightness must be between 0 and 9")
        self.write_request(VSFR.DISP_BRT, struct.pack('<B', brightness))

    def set_display_direction(self, direction: DisplayDirection) -> None:
        """Set display direction.

        Args:
            direction: Display direction
        """
        self.write_request(VSFR.DISP_DIR, struct.pack('<B', int(direction)))

    def set_vibro_ctrl(self, ctrls: List[CTRL]) -> None:
        """Set vibration control flags.

        Args:
            ctrls: List of control flags
        """
        ctrl_value = sum(int(ctrl) for ctrl in ctrls)
        self.write_request(VSFR.VIBRO_CTRL, struct.pack('<B', ctrl_value))

    def get_alarm_limits(self) -> AlarmLimits:
        """Get alarm limits.

        Returns:
            AlarmLimits object
        """
        l1_count_rate, l2_count_rate, count_unit, l1_dose_rate, l2_dose_rate, l1_dose, l2_dose, dose_unit = self.batch_read_vsfrs([
            VSFR.CR_LEV1_cp10s,
            VSFR.CR_LEV2_cp10s,
            VSFR.CR_UNITS,
            VSFR.DR_LEV1_uR_h,
            VSFR.DR_LEV2_uR_h,
            VSFR.DS_LEV1_uR,
            VSFR.DS_LEV2_uR,
            VSFR.DS_UNITS,
        ])
        
        return AlarmLimits(
            l1_count_rate=l1_count_rate,
            l2_count_rate=l2_count_rate,
            count_unit="cpm" if count_unit else "cps",
            l1_dose_rate=l1_dose_rate,
            l2_dose_rate=l2_dose_rate,
            l1_dose=l1_dose,
            l2_dose=l2_dose,
            dose_unit="R" if dose_unit else "Sv",
        )

    def set_alarm_limits(
        self,
        l1_count_rate: Optional[int | float] = None,
        l2_count_rate: Optional[int | float] = None,
        l1_dose_rate: Optional[int | float] = None,
        l2_dose_rate: Optional[int | float] = None,
        l1_dose: Optional[int | float] = None,
        l2_dose: Optional[int | float] = None,
        dose_unit_sv: Optional[bool] = None,
        count_unit_cpm: Optional[bool] = None,
    ) -> bool:
        """Set alarm limits.

        Args:
            l1_count_rate: Level 1 count rate limit
            l2_count_rate: Level 2 count rate limit
            l1_dose_rate: Level 1 dose rate limit
            l2_dose_rate: Level 2 dose rate limit
            l1_dose: Level 1 accumulated dose limit
            l2_dose: Level 2 accumulated dose limit
            dose_unit_sv: True for Sievert units, False for Roentgen
            count_unit_cpm: True for counts per minute, False for counts per second

        Returns:
            True if successful
        """
        if l1_count_rate is not None:
            self.write_request(VSFR.CR_LEV1_cp10s, struct.pack('<f', l1_count_rate))
        if l2_count_rate is not None:
            self.write_request(VSFR.CR_LEV2_cp10s, struct.pack('<f', l2_count_rate))
        if l1_dose_rate is not None:
            self.write_request(VSFR.DR_LEV1_uR_h, struct.pack('<f', l1_dose_rate))
        if l2_dose_rate is not None:
            self.write_request(VSFR.DR_LEV2_uR_h, struct.pack('<f', l2_dose_rate))
        if l1_dose is not None:
            self.write_request(VSFR.DS_LEV1_uR, struct.pack('<f', l1_dose))
        if l2_dose is not None:
            self.write_request(VSFR.DS_LEV2_uR, struct.pack('<f', l2_dose))
        if dose_unit_sv is not None:
            self.write_request(VSFR.DS_UNITS, struct.pack('<B', 0 if dose_unit_sv else 1))
        if count_unit_cpm is not None:
            self.write_request(VSFR.CR_UNITS, struct.pack('<B', 1 if count_unit_cpm else 0))
        
        return True