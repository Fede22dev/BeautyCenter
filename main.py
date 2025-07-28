import re
import sys
import time

import requests
from PySide6.QtCore import QFile, QIODeviceBase, qWarning, qDebug, QtMsgType, QTime, QLoggingCategory, \
    qInstallMessageHandler, QCommandLineOption, QCommandLineParser, qInfo, Qt, QCoreApplication, QLocale, QTranslator, \
    qCritical, QThread, QDir, QProcess, QFileInfo, QTextStream
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication, QMessageBox, QProgressDialog
from packaging import version
from tqdm import tqdm

from ui.controllers.main_window import BeautyCenterMainWindow
from utilities.utilities import qFatal, get_desktop_path

from resources.generated_qrc import styles_rc  # noqa: F401

try:
    import pyi_splash
except ImportError:
    pyi_splash = None

from name_version import APP_NAME, APP_VERSION, GITHUB_REPO_NAME

_ID_TAG = "[MAIN]"
_LOG_LEVEL = "debug"

_instance_server = QLocalServer()


def _custom_message_handler(msg_type: QtMsgType, context: str, msg: str) -> None:
    log_map = {
        QtMsgType.QtDebugMsg: (QCoreApplication.translate("main", "DEBUG"), 0),
        QtMsgType.QtInfoMsg: (QCoreApplication.translate("main", "INFO"), 1),
        QtMsgType.QtWarningMsg: (QCoreApplication.translate("main", "WARNING"), 2),
        QtMsgType.QtCriticalMsg: (QCoreApplication.translate("main", "CRITICAL"), 3),
        QtMsgType.QtFatalMsg: (QCoreApplication.translate("main", "FATAL"), 4),
    }

    log_label, level = log_map.get(msg_type, (QCoreApplication.translate("main", "UNKNOWN"), 1))
    threshold = {"debug": 0, "info": 1, "warning": 2, "critical": 3, "fatal": 4}.get(_LOG_LEVEL.lower(), 1)

    if level >= threshold:
        time_str = QTime.currentTime().toString("HH:mm:ss")
        stream = sys.stderr if level >= 2 else sys.stdout
        stream.write(f"[{time_str}] [{log_label}] {msg}\n")
        stream.flush()


# Delete the old executable if the --delete-old argument is provided
def _handle_old_exe_deletion(old_path: str) -> None:
    if not old_path:
        return

    file = QFile(old_path)

    for _ in range(5):
        if file.exists():
            if file.remove():
                message = QCoreApplication.translate("main", "Deleted old executable: {old_path}").format(
                    old_path=old_path)
                qDebug(f"{_ID_TAG} {message}")
                return
            else:
                QThread.msleep(250)
        else:
            message = QCoreApplication.translate("main", "Old executable not found: {old_path}").format(
                old_path=old_path)
            qWarning(f"{_ID_TAG} {message}")
            return

    message = QCoreApplication.translate("main", "Failed to delete old executable: {old_path}").format(
        old_path=old_path)
    qWarning(f"{_ID_TAG} {message}")


def _copy_new_exe(target_path: str) -> None:
    source_path = QDir.toNativeSeparators(QCoreApplication.applicationFilePath())
    target_path = QDir.toNativeSeparators(target_path)

    if not QFile.copy(source_path, target_path):
        if pyi_splash:
            pyi_splash.close()

        title = QCoreApplication.translate("main", "Error")
        message = QCoreApplication.translate("main", "Failed to copy new executable:\n{source_path}").format(
            source_path=source_path)
        message_log = message.replace("\n", " ").replace("  ", " ").strip()
        QMessageBox.critical(None, title, message)
        qFatal(f"{_ID_TAG} {message_log}")
    else:
        message = QCoreApplication.translate("main", "Copied new executable: {target_path}").format(
            target_path=target_path)
        qDebug(f"{_ID_TAG} {message}")


def _stop_and_run_new_exe(exe_path: str) -> None:
    current_path = QDir.toNativeSeparators(QCoreApplication.applicationFilePath())
    exe_path = QDir.toNativeSeparators(exe_path)

    args = []
    if not current_path.endswith("python.exe"):
        args = ["--delete-old", current_path]

    success = QProcess.startDetached(exe_path, args)

    if success:
        message = QCoreApplication.translate("main", "Stopped and running new executable: {exe_path}").format(
            exe_path=exe_path)
        qDebug(f"{_ID_TAG} {message}")
        sys.exit(0)
    else:
        if pyi_splash:
            pyi_splash.close()

        title = QCoreApplication.translate("main", "Error")
        message = QCoreApplication.translate("main", "Failed to stop and run new executable:\n{exe_path}").format(
            exe_path=exe_path)
        message_log = message.replace("\n", " ").replace("  ", " ").strip()
        QMessageBox.critical(None, title, message)
        qFatal(f"{_ID_TAG} {message_log}")


def _check_exe_path_desktop() -> None:
    current_exe_path = QDir.toNativeSeparators(QCoreApplication.applicationFilePath())
    desktop_path = get_desktop_path()
    exe_name = QFileInfo(current_exe_path).fileName()
    expected_path = QDir(desktop_path).filePath(exe_name)

    # Case-insensitive check (Windows-like)
    if QDir.cleanPath(current_exe_path).lower() == QDir.cleanPath(expected_path).lower():
        message = QCoreApplication.translate("main", "Executable path is correct: {current_exe_path}").format(
            current_exe_path=current_exe_path)
        qDebug(f"{_ID_TAG} {message}")
        return

    if pyi_splash:
        pyi_splash.close()

    title = QCoreApplication.translate("main", "Incorrect Executable Path")
    message = QCoreApplication.translate("main",
                                         "The executable has been moved in other dir:\nExpected: {expected_path}\nFound: {current_exe_path}\n\nThe correct path will now be restored.").format(
        expected_path=expected_path, current_exe_path=current_exe_path)
    message_log = message.replace("\n", " ").replace("  ", " ").strip()
    QMessageBox.critical(None, title, message, QMessageBox.StandardButton.Ok)
    qCritical(f"{_ID_TAG} {message_log}")

    _copy_new_exe(expected_path)
    _stop_and_run_new_exe(expected_path)


# Ensure the executable is named according to the version.
def _check_executable_name() -> None:
    expected_name = f"{APP_NAME} v. {APP_VERSION}.exe"
    current_path = QDir.toNativeSeparators(QCoreApplication.applicationFilePath())
    file_info = QFileInfo(current_path)
    current_name = file_info.fileName()
    dir_path = file_info.absolutePath()
    expected_path = QDir(dir_path).filePath(expected_name)

    if current_name == expected_name:
        message = QCoreApplication.translate("main", "Executable name is correct: {current_name}").format(
            current_name=current_name)
        qDebug(f"{_ID_TAG} {message}")
        return

    if pyi_splash:
        pyi_splash.close()

    title = QCoreApplication.translate("main", "Incorrect Executable Name")
    message = QCoreApplication.translate("main",
                                         "The executable has been renamed:\nExpected: {expected_name}\nFound: {current_name}\n\nThe correct name will now be restored.").format(
        expected_name=expected_name, current_name=current_name)
    message_log = message.replace("\n", " ").replace("  ", " ").strip()
    QMessageBox.critical(None, title, message, QMessageBox.StandardButton.Ok)
    qCritical(f"{_ID_TAG} {message_log}")

    _copy_new_exe(expected_path)
    _stop_and_run_new_exe(expected_path)


def _check_connection_quality(max_latency_ms: int = 350) -> bool:
    try:
        url = "https://www.google.com/generate_204"
        start = time.time()
        response = requests.get(url, timeout=3)
        latency = (time.time() - start) * 1000  # ms

        if response.status_code == 204 and latency <= max_latency_ms:
            message = QCoreApplication.translate("main", "Connection quality is good: {latency} ms").format(
                latency=int(latency))
            qDebug(f"{_ID_TAG} {message}")
            return True
        else:
            message = QCoreApplication.translate("main",
                                                 "Connection quality is bad, unable to check new version: {latency} ms").format(
                latency=int(latency))
            qWarning(f"{_ID_TAG} {message}")
            return False
    except Exception as e:
        message = QCoreApplication.translate("main",
                                             "Failed to check connection quality, unable to check new version: {exception}").format(
            exception=e)
        qWarning(f"{_ID_TAG} {message}")
        return False


def _check_is_latest_release() -> None:
    api_url = f"https://api.github.com/repos/{GITHUB_REPO_NAME}/releases/latest"

    data = {}
    try:
        r = requests.get(api_url, timeout=5)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        message = QCoreApplication.translate("main",
                                             "Failed to check for latest release: {api_url} Error: {exception}").format(
            api_url=api_url, exception=e)
        qWarning(f"{_ID_TAG} {message}")
        return

    asset_regex = re.compile(r"([A-Za-z0-9._ -]+)[. _]v[. _](\d+)\.(\d+)\.(\d+)\.exe$", re.IGNORECASE)
    curr_ver = version.parse(APP_VERSION)
    latest_asset = None
    latest_ver = curr_ver

    for asset in data.get("assets", []):
        match = asset_regex.match(asset.get("name", ""))
        if match:
            found_ver = ".".join(match.group(i) for i in range(2, 5))
            remote_ver = version.parse(found_ver)
            if remote_ver > curr_ver:
                latest_asset = asset
                latest_ver = remote_ver

    if not latest_asset:
        message = QCoreApplication.translate("main", "No new version found.")
        qInfo(f"{_ID_TAG} {message}")
        return

    if pyi_splash:
        pyi_splash.close()

    title = QCoreApplication.translate("main", "New Version Available")
    message = QCoreApplication.translate("main",
                                         "A new version is available:\nLocal version: {curr_ver}\nRemote version: {latest_ver}\n\nDownload now?")
    message_log = message.replace("\n", " ").replace("  ", " ").strip()
    qInfo(f"{_ID_TAG} {message_log}")
    result = QMessageBox.information(None, title, message,
                                     QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
    if result == QMessageBox.StandardButton.Cancel:
        message = QCoreApplication.translate("main", "Download cancelled.")
        qInfo(f"{_ID_TAG} {message}")
        return

    message = QCoreApplication.translate("main", "Downloading latest version...")
    qInfo(f"{_ID_TAG} {message}")

    display_name = f"{APP_NAME} v. {latest_ver}.exe"
    out_path = QDir.toNativeSeparators(QDir(get_desktop_path()).filePath(display_name))
    if QFileInfo.exists(out_path):
        _stop_and_run_new_exe(out_path)
        return

    download_url = latest_asset["browser_download_url"]
    if not download_url:
        message = QCoreApplication.translate("main", "Failed to get download URL for latest release.")
        QMessageBox.critical(None, title, message)
        qWarning(f"{_ID_TAG} {message}")
        return

    message = QCoreApplication.translate("main",
                                         "Downloading latest version {display_name} from ({download_url})").format(
        display_name=display_name, download_url=download_url)
    qInfo(f"{_ID_TAG} {message}")

    try:
        with requests.get(download_url, timeout=5, stream=True) as response:
            response.raise_for_status()
            total = int(response.headers.get('content-length', 0))

            message = QCoreApplication.translate("main",
                                                 "Downloading latest version {display_name} to ({out_path})").format(
                display_name=display_name, out_path=out_path)
            progress = QProgressDialog(message, "", 0, total)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setCancelButton(None)
            progress.setMinimumDuration(0)
            progress.setValue(0)

            with open(out_path, "wb") as file, tqdm(total=total, unit='B', unit_scale=True, unit_divisor=1024,
                                                    desc=f"Downloading {display_name}") as bar:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    QApplication.processEvents()

                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        progress.setValue(downloaded)
                        bar.update(len(chunk))

            progress.setValue(total)
    except Exception as e:
        message = QCoreApplication.translate("main", "Failed to download latest version:\n{exception}").format(
            exception=e)
        message_log = message.replace("\n", " ").replace("  ", " ").strip()
        QMessageBox.critical(None, title, message)
        qWarning(f"{_ID_TAG} {message_log}")
        return

    message = QCoreApplication.translate("main", "Downloaded latest version {display_name} to ({out_path})").format(
        display_name=display_name, out_path=out_path)
    qInfo(f"{_ID_TAG} {message}")
    _stop_and_run_new_exe(out_path)


def _check_another_instance_running(instance_server_name: str) -> bool:
    socket = QLocalSocket()
    socket.connectToServer(instance_server_name)
    if socket.waitForConnected(500):
        socket.close()
        socket.deleteLater()
        return True
    return False


def _start_local_server(instance_server_name: str) -> None:
    # Try to listen, if address busy try to remove the server and retry once
    if not _instance_server.listen(instance_server_name):
        QLocalServer.removeServer(instance_server_name)
        if not _instance_server.listen(instance_server_name):
            title = QCoreApplication.translate("main", "Error")
            message = QCoreApplication.translate("main",
                                                 "Failed to start local server:\n{instance_server_name}\nError: {error}").format(
                instance_server_name=instance_server_name, error=_instance_server.errorString())
            message_log = message.replace("\n", " ").replace("  ", " ").strip()
            QMessageBox.critical(None, title, message)
            qFatal(f"{_ID_TAG} {message_log}")


# Loads the main .ui file


def main() -> int:
    # Only reconfigure if the stream exists and supports this method (prevents crash in PyInstaller --windowed EXE)
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    if sys.stderr and hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(line_buffering=True)

    QLoggingCategory.defaultCategory().setEnabled(QtMsgType.QtDebugMsg, True)

    qInstallMessageHandler(_custom_message_handler)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    locale = QLocale.system()
    translator = QTranslator()
    if locale.language() == QLocale.Language.Italian:
        if translator.load("it.qm", "translations/generated_qm"):
            app.installTranslator(translator)
            message = QCoreApplication.translate("main", "Loaded Italian translation.")
            qDebug(f"{_ID_TAG} {message}")
        else:
            message = QCoreApplication.translate("main",
                                                 "Italian translation not found. Use default English translation.")
            qWarning(f"{_ID_TAG} {message}")

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

    _GLOBAL_LOG_LEVEL = parser.value(log_level_option)
    old_exe_path = parser.value(delete_old_option) if parser.isSet(delete_old_option) else None

    positional_args = parser.positionalArguments()
    if positional_args:
        title = QCoreApplication.translate("main", "Error")
        message = QCoreApplication.translate("main",
                                             "Unexpected positional argument(s) found:\n{positional_args}.\nUse --help or -h for usage information.").format(
            positional_args=" ".join(positional_args))
        message_log = message.replace("\n", " ").replace("  ", " ").strip()
        QMessageBox.critical(None, title, message)
        qFatal(f"{_ID_TAG} {message_log}")

    if getattr(sys, 'frozen', False):  # Exe Pyinstaller
        if old_exe_path:
            _handle_old_exe_deletion(old_exe_path)

        _check_executable_name()
        _check_exe_path_desktop()

        if _check_connection_quality():
            _check_is_latest_release()

        init_string = f"{APP_NAME} v. {APP_VERSION}"
    else:
        _GLOBAL_LOG_LEVEL = "debug"
        init_string = f"{APP_NAME} DBG v. {APP_VERSION}"

    qInfo(f"{_ID_TAG} {init_string}")

    # Check if the app is a single instance
    server_name = f"{APP_NAME}_instance"
    if _check_another_instance_running(server_name):
        if pyi_splash:
            pyi_splash.close()

        title = QCoreApplication.translate("main", "Error")
        message = QCoreApplication.translate("main", "Another instance of {app_name} is already running.").format(
            app_name=APP_NAME)
        message_log = message.replace("\n", " ").replace("  ", " ").strip()
        QMessageBox.critical(None, title, message)
        qFatal(f"{_ID_TAG} {message_log}")

    _start_local_server(server_name)

    file = QFile(":/styles/modern_pink")
    if file.open(QIODeviceBase.OpenModeFlag.ReadOnly):
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())

        message = QCoreApplication.translate("main", "Loaded style {file_name}").format(file_name=file.fileName())
        qDebug(f"{_ID_TAG} {message}")
    else:
        message = QCoreApplication.translate("main", "Failed to load style {file_name}").format(
            file_name=file.fileName())
        qWarning(f"{_ID_TAG} {message}")

    file.close()
    file.deleteLater()

    # Load and show UI
    main_window = BeautyCenterMainWindow()

    if pyi_splash:
        pyi_splash.close()

    main_window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
