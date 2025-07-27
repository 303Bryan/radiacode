"""Bytes buffer utility for the embedded Radiacode library."""

import struct
from typing import Any


class BytesBuffer:
    """A buffer for handling bytes data with structured reading capabilities."""

    def __init__(self, data: bytes):
        """Initialize the buffer with bytes data.

        Args:
            data: The bytes data to buffer
        """
        self._data = data
        self._pos = 0

    def read(self, size: int) -> bytes:
        """Read a specified number of bytes from the buffer.

        Args:
            size: Number of bytes to read

        Returns:
            The bytes read from the buffer

        Raises:
            IndexError: If trying to read beyond the buffer size
        """
        if self._pos + size > len(self._data):
            raise IndexError("Attempting to read beyond buffer size")
        
        result = self._data[self._pos:self._pos + size]
        self._pos += size
        return result

    def read_uint8(self) -> int:
        """Read an unsigned 8-bit integer.

        Returns:
            The unsigned 8-bit integer value
        """
        return struct.unpack("B", self.read(1))[0]

    def read_uint16(self) -> int:
        """Read an unsigned 16-bit integer.

        Returns:
            The unsigned 16-bit integer value
        """
        return struct.unpack("<H", self.read(2))[0]

    def read_uint32(self) -> int:
        """Read an unsigned 32-bit integer.

        Returns:
            The unsigned 32-bit integer value
        """
        return struct.unpack("<I", self.read(4))[0]

    def read_float(self) -> float:
        """Read a 32-bit float.

        Returns:
            The float value
        """
        return struct.unpack("<f", self.read(4))[0]

    def read_string(self, encoding: str = "utf-8") -> str:
        """Read a null-terminated string.

        Args:
            encoding: The string encoding to use

        Returns:
            The decoded string
        """
        end_pos = self._data.find(b'\x00', self._pos)
        if end_pos == -1:
            end_pos = len(self._data)
        
        string_data = self._data[self._pos:end_pos]
        self._pos = end_pos + 1
        return string_data.decode(encoding, errors='ignore')

    def read_bytes(self, size: int) -> bytes:
        """Read a specified number of bytes.

        Args:
            size: Number of bytes to read

        Returns:
            The bytes read
        """
        return self.read(size)

    def skip(self, size: int) -> None:
        """Skip a specified number of bytes.

        Args:
            size: Number of bytes to skip
        """
        self._pos += size

    def remaining(self) -> int:
        """Get the number of remaining bytes in the buffer.

        Returns:
            Number of remaining bytes
        """
        return len(self._data) - self._pos

    def at_end(self) -> bool:
        """Check if the buffer position is at the end.

        Returns:
            True if at the end of the buffer
        """
        return self._pos >= len(self._data)

    def get_data(self) -> bytes:
        """Get the complete buffer data.

        Returns:
            The complete buffer data
        """
        return self._data

    def get_position(self) -> int:
        """Get the current position in the buffer.

        Returns:
            The current position
        """
        return self._pos

    def set_position(self, pos: int) -> None:
        """Set the position in the buffer.

        Args:
            pos: The new position
        """
        if pos < 0 or pos > len(self._data):
            raise IndexError("Position out of bounds")
        self._pos = pos