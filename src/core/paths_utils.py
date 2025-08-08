import sys

from PySide6.QtCore import QDir, QCoreApplication, QStandardPaths, qDebug, QFileInfo, qWarning, QThread, \
    QFile

from src.core.logging_utils import show_box_critical_and_log
from src.core.process_utils import _stop_and_run_new_exe, _copy_at_new_path_exe
from src.name_version import APP_NAME, APP_VERSION

_ID_TAG = "[APP_PATH_UTILS]"


# Delete the old executable if the --delete-old argument is provided
def handle_old_exe_deletion(old_path: str) -> None:
    if not old_path:
        return

    file = QFile(old_path)

    for _ in range(5):
        if not file.exists():
            message = QCoreApplication.translate("app_path_utils", "Old executable not found: {old_path}").format(
                old_path=old_path)
            qWarning(f"{_ID_TAG} {message}")
            return

        if file.remove():
            qDebug(f"{_ID_TAG} Deleted old executable: {old_path}")
            return

        QThread.msleep(250)

    message = QCoreApplication.translate("app_path_utils", "Failed to delete old executable: {old_path}").format(
        old_path=old_path)
    qWarning(f"{_ID_TAG} {message}")


# Ensure the executable is named according to the version.
def check_executable_name() -> None:
    expected_name = f"{APP_NAME} v. {APP_VERSION}.exe"
    current_path = QDir.toNativeSeparators(QCoreApplication.applicationFilePath())
    file_info = QFileInfo(current_path)

    current_name = file_info.fileName()
    dir_path = file_info.absolutePath()
    expected_path = QDir(dir_path).filePath(expected_name)

    if current_name == expected_name:
        qDebug(f"{_ID_TAG} Executable name is correct: {current_name}")
        return

    title = QCoreApplication.translate("app_path_utils", "Incorrect Executable Name")
    message = QCoreApplication.translate("app_path_utils",
                                         "The executable has been renamed:\nExpected: {expected_name}\nFound: {current_name}\n\nThe correct name will now be restored.").format(
        expected_name=expected_name, current_name=current_name)
    show_box_critical_and_log(_ID_TAG, title, message)

    _copy_at_new_path_exe(expected_path)
    _stop_and_run_new_exe(expected_path)


def check_exe_path_desktop() -> None:
    current_exe_path = QDir.toNativeSeparators(QCoreApplication.applicationFilePath())
    desktop_path = _get_desktop_path()
    exe_name = QFileInfo(current_exe_path).fileName()
    expected_exe_path = QDir(desktop_path).filePath(exe_name)

    # Case-insensitive check (Windows-like)
    if QDir.cleanPath(current_exe_path).lower() == QDir.cleanPath(expected_exe_path).lower():
        qDebug(f"{_ID_TAG} Executable path is correct: {current_exe_path}")
        return

    title = QCoreApplication.translate("app_path_utils", "Incorrect Executable Path")
    message = QCoreApplication.translate("app_path_utils",
                                         "The executable has been moved in other dir:\nExpected: {expected_exe_path}\nFound: {current_exe_path}\n\nThe correct path will now be restored.").format(
        expected_exe_path=expected_exe_path, current_exe_path=current_exe_path)
    show_box_critical_and_log(_ID_TAG, title, message)

    _copy_at_new_path_exe(expected_exe_path)
    _stop_and_run_new_exe(expected_exe_path)


# Get an absolute path to resource (compatible with PyInstaller).
# Can use it for a single file or also for a directory
def get_resource_path(relative_path: str) -> str:
    base_path = getattr(sys, '_MEIPASS', QDir.currentPath())
    return QDir(base_path).filePath(relative_path)


def _get_desktop_path() -> str:
    desktop = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
    if not desktop:
        home = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation)
        desktop = QDir(home).filePath("Desktop")

    return QDir.toNativeSeparators(desktop)
