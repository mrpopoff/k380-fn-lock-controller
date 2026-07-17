# K380 Fn Lock Controller

A Python port of [dheygere/k380-fn-lock-for-windows].
Module to control Fn Lock mode on the Logitech K380 keyboard.

## Goal

This program sets the function keys for the Logitech K380 bluetooth keyboard.
Having the F1-F12 without pressing the Fn key is nice for developers.

A simple way to do the same as the Logitech Options/Options+ software WITHOUT their continuously running processes.

## Features

- Enable/disable Fn Lock mode via command line or Python API
- Simple context manager for safe device handling
- Support for multiple K380 devices (first found is used by default)

## Requirements

- Python 3.10+
- [hidapi] library
- Logitech K380 Multi-Device Bluetooth Keyboard connected

## Installation

### From source (editable install)

```bash
git clone https://github.com/mrpopoff/k380-fn-lock-controller.git
cd k380-fn-lock-controller
pip install -e .
```

### From source (system-wide)

```bash
git clone https://github.com/mrpopoff/k380-fn-lock-controller.git
cd k380-fn-lock-controller
pip install .
```

## Usage

### Command Line

After installation, use the k380-ctl command:

```bash
# Enable Fn Lock (function keys as default till next reboot)
k380-ctl --fn-keys
k380-ctl -f
```

```bash
# Disable Fn Lock (restore media keys as default)
k380-ctl --media-keys
k380-ctl -m
```

### As a Python Module

```python
from k380_controller import K380Device, K380Mode

# Using context manager (ensures proper device cleanup)
with K380Device() as k380:
    k380.print_info()
    k380.set_mode(K380Mode.K380_MODE_FN_KEYS)
```

## Module Structure

```pre
k380_controller/
├── __init__.py          # Public API exports
├── __main__.py          # Entry point for `python -m k380_controller`
├── cli.py               # Command-line interface
├── core.py              # Core HID device logic
└── py.typed             # PEP 561 marker for type checking
```

## Constants

| Constant | Value | Description |
| ---------- | ----- | ----------- |
| `K380_VID` | `1133` (0x46D) | USB Vendor ID |
| `K380_PID` | `45890` (0xB342) | USB Product ID |
| `K380_TARGET_USAGE` | `1` | HID interface usage |
| `K380_TARGET_USAGE_PAGE` | `65280` | HID interface usage page |

## Error Handling

The module defines custom exceptions:

- `K380Error` - base exception class
- `DeviceNotFoundError` - raised when no K380 device is found
- `DeviceConnectionError` - raised when device connection fails
- `DeviceCommunicationError` - raised when device read/write operation fails

## Known Issues

The `OSError: open failed` error originating from `hid.pyx` happens when the Python `hidapi` wrapper cannot establish a connection to your USB or Bluetooth device. Because the underlying C library is uninformative, it abstracts many potential issues into this single error.

### 1. Insufficient Permissions (Linux & Raspberry Pi)

By default, Linux restricts direct read/write access to raw hardware devices for non-root users.

- **Quick Test:** Run command with root privileges:
```bash
sudo k380-ctl -f
```

- **Permanent Fix:** If sudo works, create a custom udev rule so you do not have to run as root. Create a file named /etc/udev/rules.d/99-hidapi.rules and paste this line inside:
```bash
KERNEL=="hidraw*", SUBSYSTEM=="hidraw", MODE="0666", TAG+="uaccess"
```
Reload the rules to apply changes:
```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### 2. Another Application is Locking the Device

HID devices often allow only a single, exclusive application layer to lock the interface. Ensure proprietary Logitech software associated with your device is completely shut down.

### 3. Grant Input Monitoring Permissions (MacOS)

If you are trying to intercept input events on a Mac, you must grant permissions in System Settings:
- Go to **System Settings > Privacy & Security > Input Monitoring**.
- Add your Terminal app or Python IDE to the list and toggle it ON.

## License

MIT License

## References

- [dheygere/k380-fn-lock-for-windows]
- [hidapi]

---
Nikita A. Popov <<n.popov.79@gmail.com>> 2026

[dheygere/k380-fn-lock-for-windows]: https://github.com/dheygere/k380-fn-lock-for-windows/
[hidapi]: https://pypi.org/project/hidapi/