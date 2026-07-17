"""
K380 Fn Lock Controller

Module for controlling the Fn Lock mode on the Logitech K380 keyboard.
"""

from k380_controller.core import (
    K380Device,
    K380Mode,
    K380Error,
    DeviceNotFoundError,
    DeviceConnectionError,
    DeviceCommunicationError,
    K380_VID,
    K380_PID,
    K380_TARGET_USAGE,
    K380_TARGET_USAGE_PAGE
)

__version__ = "1.0.0"

__all__ = [
    "K380Device",
    "K380Mode",
    "K380Error",
    "DeviceNotFoundError",
    "DeviceConnectionError",
    "DeviceCommunicationError",
    "K380_VID",
    "K380_PID",
    "K380_TARGET_USAGE",
    "K380_TARGET_USAGE_PAGE"
]
