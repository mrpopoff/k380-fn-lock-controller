# pylint: disable=missing-docstring

import unittest
import unittest.mock

from k380_controller import (
    K380_VID,
    K380_PID,
    K380_TARGET_USAGE,
    K380_TARGET_USAGE_PAGE,
    K380Device,
    K380Mode,
    DeviceNotFoundError,
    DeviceConnectionError,
    DeviceCommunicationError
)
from k380_controller.core import K380_SEQ_FKEYS_ON, K380_SEQ_FKEYS_OFF


@unittest.mock.patch("k380_controller.core.hid")
class TestK380Device(unittest.TestCase):

    def setUp(self):
        self.mock_data = [
            {
                "usage": K380_TARGET_USAGE,
                "usage_page": K380_TARGET_USAGE_PAGE,
                "path": "foo"
            }
        ]


    def test_open(self, mock_hid):
        mock_hid.enumerate.return_value = self.mock_data

        with K380Device() as device:
            mock_hid.enumerate.assert_called_once_with(K380_VID, K380_PID)
            mock_hid.device.assert_called_once()
            mock_hid.device.return_value.open_path.assert_called_once_with("foo")

            self.assertEqual(device.vid, K380_VID)
            self.assertEqual(device.pid, K380_PID)
            self.assertEqual(device.path, "foo")
            self.assertTrue(device.is_open)

        mock_hid.device.return_value.close.assert_called_once()
        self.assertFalse(device.is_open)


    def test_open_opened(self, mock_hid):
        mock_hid.enumerate.return_value = self.mock_data

        with K380Device() as device:
            self.assertTrue(device.is_open)
            with self.assertRaisesRegex(DeviceConnectionError, "Device is already open"):
                device.open(path="bar")
        self.assertFalse(device.is_open)


    def test_open_path(self, mock_hid):
        mock_hid.enumerate.return_value = self.mock_data

        with K380Device(path="bar") as device:
            mock_hid.device.assert_called_once()
            mock_hid.device.return_value.open_path.assert_called_once_with("bar")

            self.assertEqual(device.vid, K380_VID)
            self.assertEqual(device.pid, K380_PID)
            self.assertEqual(device.path, "bar")
            self.assertTrue(device.is_open)

        self.assertFalse(device.is_open)


    def test_open_error(self, mock_hid):
        mock_hid.enumerate.return_value = self.mock_data
        mock_hid.device.return_value.open_path.side_effect = OSError("open failed")

        device = K380Device()
        with self.assertRaisesRegex(DeviceConnectionError, "Failed to open device: open failed"):
            device.open()
        self.assertFalse(device.is_open)


    def test_open_not_found(self, mock_hid):
        mock_hid.enumerate.return_value = []

        device = K380Device(vid=1234, pid=5678)
        with self.assertRaisesRegex(DeviceNotFoundError, "K380 device not found"):
            device.open()
            self.assertFalse(device.is_open)
        self.assertFalse(device.is_open)


    def test_close(self, mock_hid):
        mock_hid.enumerate.return_value = self.mock_data

        with K380Device() as device:
            self.assertTrue(device.is_open)
            device.close()
            self.assertFalse(device.is_open)

        mock_hid.device.return_value.close.assert_called_once()
        self.assertFalse(device.is_open)


    def test_set_mode_fn_keys(self, mock_hid):
        mock_hid.enumerate.return_value = self.mock_data
        mock_hid.device.return_value.write.return_value = 7

        with K380Device() as device:
            self.assertTrue(device.is_open)
            device.set_mode(mode=K380Mode.K380_MODE_FN_KEYS)

            mock_hid.device.return_value.write.assert_called_once_with(K380_SEQ_FKEYS_ON)

        self.assertFalse(device.is_open)


    def test_set_mode_media_keys(self, mock_hid):
        mock_hid.enumerate.return_value = self.mock_data
        mock_hid.device.return_value.write.return_value = 7

        with K380Device() as device:
            self.assertTrue(device.is_open)
            device.set_mode(mode=K380Mode.K380_MODE_MEDIA_KEYS)

            mock_hid.device.return_value.write.assert_called_once_with(K380_SEQ_FKEYS_OFF)

        self.assertFalse(device.is_open)


    def test_set_mode_error(self, mock_hid):
        mock_hid.enumerate.return_value = self.mock_data
        mock_hid.device.return_value.write.return_value = -1

        with K380Device() as device:
            self.assertTrue(device.is_open)
            with self.assertRaisesRegex(DeviceCommunicationError, "Device write failed"):
                device.set_mode(mode=K380Mode.K380_MODE_FN_KEYS)
        self.assertFalse(device.is_open)


    def test_set_fn_lock_on(self, mock_hid):
        mock_hid.enumerate.return_value = self.mock_data
        mock_hid.device.return_value.write.return_value = 7

        with K380Device() as device:
            self.assertTrue(device.is_open)
            device.set_fn_lock(enabled=True)

            mock_hid.device.return_value.write.assert_called_once_with(K380_SEQ_FKEYS_ON)


    def test_set_fn_lock_off(self, mock_hid):
        mock_hid.enumerate.return_value = self.mock_data
        mock_hid.device.return_value.write.return_value = 7

        with K380Device() as device:
            self.assertTrue(device.is_open)
            device.set_fn_lock(enabled=False)

            mock_hid.device.return_value.write.assert_called_once_with(K380_SEQ_FKEYS_OFF)
