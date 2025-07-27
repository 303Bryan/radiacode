"""Spectrum decoder for the embedded Radiacode library."""

import datetime
import struct
from typing import List

from ..bytes_buffer import BytesBuffer
from ..types import Spectrum


def decode_counts_v0(br: BytesBuffer) -> List[int]:
    """Decode spectrum counts using version 0 format.

    Args:
        br: BytesBuffer containing the count data

    Returns:
        List of count values
    """
    ret = []
    while br.remaining() > 0:
        ret.append(br.read_uint32())
    return ret


def decode_counts_v1(br: BytesBuffer) -> List[int]:
    """Decode spectrum counts using version 1 format.

    Args:
        br: BytesBuffer containing the count data

    Returns:
        List of count values

    Raises:
        Exception: If unsupported vlen value is encountered
    """
    ret = []
    last = 0
    
    while br.remaining() > 0:
        u16 = br.read_uint16()
        cnt = (u16 >> 4) & 0x0FFF
        vlen = u16 & 0x0F
        
        for _ in range(cnt):
            if vlen == 0:
                v = 0
            elif vlen == 1:
                v = br.read_uint8()
            elif vlen == 2:
                v = last + struct.unpack('<b', br.read(1))[0]
            elif vlen == 3:
                v = last + struct.unpack('<h', br.read(2))[0]
            elif vlen == 4:
                a, b, c = struct.unpack('<BBb', br.read(3))
                v = last + ((c << 16) | (b << 8) | a)
            elif vlen == 5:
                v = last + struct.unpack('<i', br.read(4))[0]
            else:
                raise Exception(f'unsupported vlen={vlen} in decode_RC_VS_SPECTRUM version=1')

            last = v
            ret.append(v)
    
    return ret


def decode_RC_VS_SPECTRUM(br: BytesBuffer, format_version: int) -> Spectrum:
    """Decode RC_VS_SPECTRUM data from the device.

    Args:
        br: BytesBuffer containing the spectrum data
        format_version: Format version (0 or 1)

    Returns:
        Spectrum object containing the decoded data

    Raises:
        Exception: If unsupported format version is encountered
    """
    ts, a0, a1, a2 = struct.unpack('<Ifff', br.read(16))

    if format_version not in {0, 1}:
        raise Exception(f'unsupported format_version={format_version}')
    
    counts = decode_counts_v0(br) if format_version == 0 else decode_counts_v1(br)

    return Spectrum(
        duration=datetime.timedelta(seconds=ts),
        a0=a0,
        a1=a1,
        a2=a2,
        counts=counts,
    )