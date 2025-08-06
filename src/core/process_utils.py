import sys

from PySide6.QtCore import QDir, QCoreApplication, QFile, qDebug, QProcess

from src.core.logging_utils import show_box_critical_and_log

_ID_TAG = "[HELPER]"


def _copy_at_new_path_exe(target_path: str) -> None:
    source_path = QDir.toNativeSeparators(QCoreApplication.applicationFilePath())
    target_path = QDir.toNativeSeparators(target_path)

    if not QFile.copy(source_path, target_path):
        title = QCoreApplication.translate("helper", "Error")
        message = QCoreApplication.translate("helper", "Failed to copy new executable:\n{source_path}").format(
            source_path=source_path)
        show_box_critical_and_log(_ID_TAG, title, message, True)
    else:
        qDebug(f"{_ID_TAG} Copied new executable at: {target_path}")


def _stop_and_run_new_exe(exe_path: str) -> None:
    current_path = QDir.toNativeSeparators(QCoreApplication.applicationFilePath())
    exe_path = QDir.toNativeSeparators(exe_path)

    args = ["--delete-old", current_path] if not current_path.endswith("python.exe") else []

    if QProcess.startDetached(exe_path, args):
        qDebug(f"{_ID_TAG} Stopped and running new executable: {exe_path}")
        sys.exit(0)
    else:
        title = QCoreApplication.translate("main", "Error")
        message = QCoreApplication.translate("main", "Failed to stop and run new executable:\n{exe_path}").format(
            exe_path=exe_path)
        show_box_critical_and_log(_ID_TAG, title, message, True)
