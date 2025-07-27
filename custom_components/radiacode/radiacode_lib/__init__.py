"""Embedded Radiacode Library for Home Assistant Integration

This module provides a self-contained Python interface for controlling RadiaCode 
radiation detection devices via USB or Bluetooth connections. It supports device 
configuration, data acquisition, and spectrum analysis.
"""

from .radiacode import RadiaCode
from .types import (
    RealTimeData,
    RareData,
    Spectrum,
    AlarmLimits,
    DisplayDirection,
    DoseRateDB,
    Event,
    RawData,
    COMMAND,
    CTRL,
    VS,
    VSFR,
)

__all__ = [
    "RadiaCode",
    "RealTimeData",
    "RareData", 
    "Spectrum",
    "AlarmLimits",
    "DisplayDirection",
    "DoseRateDB",
    "Event",
    "RawData",
    "COMMAND",
    "CTRL",
    "VS",
    "VSFR",
]