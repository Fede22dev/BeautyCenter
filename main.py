import errno
import os
import re
import shutil
import subprocess
import sys
import time

import requests
from PySide6.QtCore import QFile, QIODeviceBase, qWarning, qDebug, QtMsgType, QTime, QLoggingCategory, \
    qInstallMessageHandler, QCommandLineOption, QCommandLineParser, qInfo
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget
from packaging import version

from utilities.utilities import qFatal, get_resource_path

try:
    import pyi_splash
except ImportError:
    pyi_splash = None

from name_version import APP_NAME, APP_VERSION, GITHUB_REPO_NAME

_ID_TAG = "[MAIN]"

_LOG_LEVEL = "debug"

_instance_server = None


def _custom_message_handler(msg_type, context, msg):
    log_map = {
        QtMsgType.QtDebugMsg: ("DEBUG", 0),
        QtMsgType.QtInfoMsg: ("INFO", 1),
        QtMsgType.QtWarningMsg: ("WARNING", 2),
        QtMsgType.QtCriticalMsg: ("CRITICAL", 3),
        QtMsgType.QtFatalMsg: ("FATAL", 4),
    }

    log_label, level = log_map.get(msg_type, ("UNKNOWN", 1))
    threshold = {"debug": 0, "info": 1, "warning": 2, "critical": 3, "fatal": 4}.get(_LOG_LEVEL.lower(), 1)

    if level >= threshold:
        time_str = QTime.currentTime().toString("HH:mm:ss")
        output = sys.stderr if level >= 2 else sys.stdout
        output.write(f"[{time_str}] [{log_label}] {msg}\n")
        output.flush()

    if msg_type == QtMsgType.QtFatalMsg:
        sys.exit(1)


def _is_latest_release():
    url = f"https://api.github.com/repos/{GITHUB_REPO_NAME}/releases"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"GitHub request error: {e}")
        return None

    try:
        releases = response.json()
    except Exception as e:
        print(f"Invalid JSON from GitHub: {e}")
        return None

    current_version = version.parse(APP_VERSION)
    latest_version = current_version
    latest_asset_url = None
    # Adjusted regex for "Beauty Center v. 0.1.0.exe" (captures a version with possible spaces and optional v)
    asset_regex = re.compile(r'Beauty Center v[.\s]*([\d.]+)\.exe', re.IGNORECASE)

    for release in releases:
        for asset in release.get("assets", []):
            name = asset.get("name", "")
            match = asset_regex.match(name)
            if match:
                remote_ver = version.parse(match.group(1))
                if remote_ver > latest_version:
                    latest_version = remote_ver
                    latest_asset_url = asset["browser_download_url"]

    if latest_asset_url:
        print(f"New version available: {latest_version}")
        return latest_asset_url
    else:
        print("You are already up to date")
        return None


# Delete the old executable if the --delete-old argument is provided
def _handle_old_exe_deletion(old_path: str):
    if not old_path:
        return

    for _ in range(5):
        try:
            if os.path.exists(old_path):
                os.remove(old_path)
                qDebug(f"{_ID_TAG} Deleted old executable: {old_path}")
            else:
                qWarning(f"{_ID_TAG} Old executable not found: {old_path}")
            return
        except OSError as e:
            if e.errno in (errno.EACCES, errno.ENOENT):
                time.sleep(0.2)
            else:
                qWarning(f"{_ID_TAG} Failed to delete old executable: {e}")
                return

    qFatal(f"{_ID_TAG} Could not delete old executable after many retries: {old_path}")


# Ensure the executable is named according to the version.
def _verify_executable_name():
    expected_name = f"{APP_NAME} v. {APP_VERSION}.exe"
    current_path = os.path.abspath(sys.executable)
    current_name = os.path.basename(current_path)
    expected_path = os.path.join(os.path.dirname(current_path), expected_name)

    if current_name == expected_name:
        qDebug("Executable name is correct.")
        return

    # Notify user about the rename
    QMessageBox.critical(
        None,
        "Incorrect Executable Name",
        f"The executable has been renamed:\nExpected: {expected_name}\nFound: {current_name}\n\n"
        "The correct name will now be restored.",
        QMessageBox.StandardButton.Ok
    )

    try:
        shutil.copy2(current_path, expected_path)
        subprocess.Popen([expected_path, "--delete-old", current_path])
        qDebug("New executable launched. Exiting current process.")
        sys.exit(0)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to copy/launch executable:\n{e}")
        qFatal(f"{_ID_TAG} Failed to rename or launch correct executable: {e}")


def _is_another_instance_running(instance_server_name: str) -> bool:
    socket = QLocalSocket()
    socket.connectToServer(instance_server_name)
    if socket.waitForConnected(500):
        socket.close()
        return True
    return False


def _start_local_server(instance_server_name: str):
    global _instance_server
    _instance_server = QLocalServer()
    # Try to listen, if address busy try to remove the server and retry once
    if not _instance_server.listen(instance_server_name):
        QLocalServer.removeServer(instance_server_name)
        if not _instance_server.listen(instance_server_name):
            qFatal(f"{_ID_TAG} Failed to start local server: {_instance_server.errorString()}")


# Loads the main .ui file
def _load_main_window() -> QWidget:
    loader = QUiLoader()
    ui_path = get_resource_path("ui/main_window/main_window.ui")
    ui_file = QFile(ui_path)

    if not ui_file.open(QIODeviceBase.OpenModeFlag.ReadOnly):
        qFatal(f"{_ID_TAG} Cannot open UI file: {ui_path} | {ui_file.errorString()}")

    main_window = loader.load(ui_file)
    ui_file.close()

    if not main_window:
        qFatal(f"{_ID_TAG} Failed to load UI: {loader.errorString()}")

    return main_window


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

    QLoggingCategory.defaultCategory().setEnabled(QtMsgType.QtDebugMsg, True)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    parser = QCommandLineParser()
    parser.setApplicationDescription(APP_NAME)
    parser.addHelpOption()  # Add -h / --help
    parser.addVersionOption()  # Add -v / --version
    log_level_option = QCommandLineOption(["log-level"],  # Add --log-level
                                          "Set log level (debug, info, warning, critical, fatal). Info is the default.",
                                          "level",  # Name expected value es. --log-level debug
                                          "info")  # Default level info
    parser.addOption(log_level_option)
    delete_old_option = QCommandLineOption(["delete-old"],  # Add --delete-old
                                           "Delete the old executable if the --delete-old argument is provided.",
                                           "path")
    delete_old_option.setFlags(QCommandLineOption.Flag.HiddenFromHelp)
    parser.addOption(delete_old_option)
    parser.process(app)

    _LOG_LEVEL = parser.value(log_level_option)
    old_exe_path = parser.value(delete_old_option) if parser.isSet(delete_old_option) else None

    qInstallMessageHandler(_custom_message_handler)

    positional_args = parser.positionalArguments()
    if positional_args:
        qFatal(
            f"{_ID_TAG} {APP_NAME} unexpected positional argument(s) found: {" ".join(positional_args)}. Use --help or -h for usage information.")

        _is_latest_release()

    if getattr(sys, 'frozen', False):  # Exe Pyinstaller
        _verify_executable_name()

        if old_exe_path:
            _handle_old_exe_deletion(old_exe_path)

        init_string = f"{APP_NAME} v. {APP_VERSION}"
    else:
        _LOG_LEVEL = "debug"
        qDebug("Executable name check skipped, not exe pyinstaller.")
        init_string = f"{APP_NAME} DBG v. {APP_VERSION}"

    qInfo(f"{_ID_TAG} {init_string}")

    # Check if the app is a single instance
    server_name = f"{APP_NAME}_instance"
    if _is_another_instance_running(server_name):
        QMessageBox.critical(None, f"{_ID_TAG} App Error", f"{APP_NAME} is already running in another window.")
        qFatal(f"{_ID_TAG} {APP_NAME} is already running.")

    _start_local_server(server_name)

    # Load and show UI
    window = _load_main_window()
    if pyi_splash:
        pyi_splash.close()

    window.show()
    sys.exit(app.exec())
