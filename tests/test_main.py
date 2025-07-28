import unittest
from unittest.mock import patch, MagicMock

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QMessageBox

from main import _check_is_latest_release


class TestCheckIsLatestRelease(unittest.TestCase):

    @patch("main.requests.get")
    @patch("main.QMessageBox.information")
    @patch("main.QFileInfo.exists")
    @patch("main._stop_and_run_new_exe")
    def test_no_new_version_found(self, mock_stop_and_run, mock_file_exists, mock_message_box, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "assets": [{"name": "example_v1.0.0.exe"}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with patch("main.version.parse", side_effect=lambda v: v):
            _check_is_latest_release()

        mock_message_box.assert_not_called()
        mock_stop_and_run.assert_not_called()

    @patch("main.requests.get")
    def test_api_request_fails(self, mock_get):
        mock_get.side_effect = Exception("Request failed")
        with patch("main.qWarning") as mock_warning:
            _check_is_latest_release()
        mock_warning.assert_called_once()

    @patch("main.requests.get")
    @patch("main.QMessageBox.information")
    @patch("main.version.parse")
    def test_new_version_available(self, mock_version_parse, mock_message_box, mock_get):
        mock_version_parse.side_effect = lambda v: v
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "assets": [{"name": "Beauty Center v. 2.0.0.exe"}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        mock_message_box.return_value = QMessageBox.StandardButton.Ok

        with patch("main.qInfo") as mock_info:
            _check_is_latest_release()
        mock_info.assert_called()


if __name__ == "__main__":
    QCoreApplication.setApplicationName("TestApp")
    QCoreApplication.setApplicationVersion("1.0.0")
    unittest.main()
