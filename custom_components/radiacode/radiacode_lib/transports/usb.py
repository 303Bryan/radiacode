"""USB transport for the embedded Radiacode library."""

import struct
import usb.core
from typing import Optional

from ..bytes_buffer import BytesBuffer


class DeviceNotFound(Exception):
    """Raised when the Radiacode device is not found."""
    pass


class MultipleUSBReadFailure(Exception):
    """Raised when max. number of USB read failures reached."""

    def __init__(self, message=None):
        self.message = 'Multiple USB Read Failures' if message is None else message
        super().__init__(self.message)


class Usb:
    """USB transport for Radiacode devices."""

    def __init__(self, serial_number: Optional[str] = None, timeout_ms: int = 3000):
        """Initialize USB transport.

        Args:
            serial_number: Optional serial number to connect to specific device
            timeout_ms: USB timeout in milliseconds
        """
        _vid = 0x0483
        _pid = 0xF123

        if serial_number:
            self._device = usb.core.find(idVendor=_vid, idProduct=_pid, serial_number=serial_number)
        else:
            # usb.core.find(..., serial_number=None) will attempt to match against a value of None,
            # rather than ignoring it as a match condition.
            self._device = usb.core.find(idVendor=_vid, idProduct=_pid)
        
        self._timeout_ms = timeout_ms
        
        if self._device is None:
            raise DeviceNotFound("Radiacode device not found")
        
        # Clear any pending data
        while True:
            try:
                self._device.read(0x81, 256, timeout=100)
            except usb.core.USBTimeoutError:
                break

    def execute(self, request: bytes) -> BytesBuffer:
        """Execute a USB request.

        Args:
            request: The request bytes to send

        Returns:
            BytesBuffer containing the response

        Raises:
            MultipleUSBReadFailure: If multiple USB read failures occur
        """
        self._device.write(0x1, request)

        trials = 0
        max_trials = 3
        while trials < max_trials:  # repeat until non-zero length data received
            data = self._device.read(0x81, 256, timeout=self._timeout_ms).tobytes()
            if len(data) != 0:
                break
            else:
                trials += 1
        
        if trials >= max_trials:
            raise MultipleUSBReadFailure(f'{trials} USB Read Failures in sequence')

        response_length = struct.unpack_from('<I', data)[0]
        data = data[4:]

        while len(data) < response_length:
            r = self._device.read(0x81, response_length - len(data)).tobytes()
            data += r

        return BytesBuffer(data)