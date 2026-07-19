"""K380 keyboard core HID device logic."""

from __future__ import annotations
from enum import Enum

import hid
from typing import Iterator

# K380 Vendor ID / Product ID
K380_VID: int = 1133  # 0x46D
K380_PID: int = 45890  # 0xB342

# Usage page values and magic sequences from dheygere/k380-fn-lock-for-windows (MIT)

# K380 HID interface usage
K380_TARGET_USAGE: int = 1
K380_TARGET_USAGE_PAGE: int = 65280

# K380 Fn Lock mode toggle magic sequences 
K380_SEQ_FKEYS_ON: list[int] = [0x10, 0xFF, 0x0B, 0x1E, 0x00, 0x00, 0x00]
K380_SEQ_FKEYS_OFF: list[int] = [0x10, 0xFF, 0x0B, 0x1E, 0x01, 0x00, 0x00]


class K380Mode(Enum):
    """K380 keyboard F-keys default mode"""
    K380_MODE_FN_KEYS = "fn-keys"
    """Fn keys triggered by default"""
    K380_MODE_MEDIA_KEYS = "media-keys"
    """Media keys triggered by default"""


class K380Error(Exception):
    """Base exception."""
    pass


class DeviceNotFoundError(K380Error):
    """Raised when no K380 device is found."""
    pass


class DeviceConnectionError(K380Error):
    """Raised when device connection fails."""
    pass


class DeviceCommunicationError(K380Error):
    """Raised when device write fails."""
    pass


def _filter_usage_func(dev: dict) -> bool:
    """Verify HID device descriptor  K380."""
    return (
        K380_TARGET_USAGE == dev.get("usage", -1)
        and K380_TARGET_USAGE_PAGE == dev.get("usage_page", -1)
    )


def find_k380_devices(vid: int = K380_VID, pid: int = K380_PID) -> Iterator[dict]:
    """K380 devices generator."""
    for dev_dict in hid.enumerate(vid, pid):
        if _filter_usage_func(dev_dict):
            yield dev_dict


class K380Device:
    """
    Logitech K380 keyboard device context manager.
    
    Usage:
        with K380Device() as k380:
            k380.set_mode(K380Mode.K380_MODE_FN_KEYS)
    """
    
    def __init__(
        self,
        vid: int = K380_VID,
        pid: int = K380_PID,
        path: str | None = None,
    ) -> None:
        self.vid = vid
        self.pid = pid
        self._device: hid.device | None = None
        self._path = path

    def _ensure_open(self) -> hid.device:
        if self._device is None:
            raise DeviceConnectionError("Device is not open. Use 'open()' first.")
        return self._device

    def open(self, path: str | None = None) -> K380Device:
        """
        Open a connection to the Logitech K380 device.
        
        Args:
            path: K380 device path. Opens first found device if None.

        Returns:
            K380Device: An instance representing the connected K380 device.

        Raises:
            DeviceNotFoundError: If the device was not found.
            DeviceConnectionError: If connection to the device could not be established or was not completed successfully.
        """
        path = path if path is not None else self._path

        if path is None:
            for dev in find_k380_devices(self.vid, self.pid):
                path = dev["path"]
                break
            else:
                raise DeviceNotFoundError("K380 device not found")

        try:
            self._device = hid.device()
            self._device.open_path(path)         
        except OSError as e:
            self._device = None
            raise DeviceConnectionError(f"Failed to open device: {e}") from e

        self._path = path

        return self

    def close(self) -> None:
        """Close device."""
        if self._device is not None:
            self._device.close()
            self._device = None

    def __enter__(self) -> K380Device:
        self.open(self._path)
        return self

    def __exit__(self, *args) -> None:
        self.close()

    @property
    def is_open(self) -> bool:
        """Ensure if device is opened."""
        return self._device is not None

    def get_info(self) -> dict:
        """
        Returns device description.
        
        Returns:
            dict with keys: manufacturer, product, serial
        """
        hiddev = self._ensure_open()
        return {
            "manufacturer": hiddev.get_manufacturer_string(),
            "product": hiddev.get_product_string(),
            "serial": hiddev.get_serial_number_string(),
        }

    def _write(self, sequence: list[int]) -> None:
        """Send commands to device."""
        hiddev = self._ensure_open()
        bytes_written: int = hiddev.write(sequence)
        if bytes_written != len(sequence):
            raise DeviceCommunicationError(f"Device write failed, result: {bytes_written}")

    def set_fn_lock(self, enabled: bool) -> None:
        """
        On/off Fn Lock.
        
        Args:
            enabled: True — Fn Lock On (F-keys by default),
                     False — Fn Lock Off (Media-keys by default)
        """
        sequence = K380_SEQ_FKEYS_ON if enabled else K380_SEQ_FKEYS_OFF
        self._write(sequence)

    def set_mode(self, mode: K380Mode) -> None:
        """
        Sets F1-F12 keys handling mode.
        
        Args:
            mode: K380_MODE_FN_KEYS or K380_MODE_MEDIA_KEYS
        
        Raises:
            ValueError: If mode is unknown
        """
        match mode:
            case K380Mode.K380_MODE_FN_KEYS:
                self.set_fn_lock(True)
            case K380Mode.K380_MODE_MEDIA_KEYS:
                self.set_fn_lock(False)
            case _:
                raise ValueError(f"Unknown mode: {mode!r}. "
                                 f"Use K380_MODE_FN_KEYS or K380_MODE_MEDIA_KEYS")

    def print_info(self) -> None:
        """Prints device description to stdout."""
        info = self.get_info()
        print(f"Manufacturer: {info['manufacturer']}")
        print(f"Product: {info['product']}")
        print(f"Serial No: {info['serial']}")
