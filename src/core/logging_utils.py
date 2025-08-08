import sys
from enum import StrEnum

from PySide6.QtCore import QtMsgType, QCoreApplication, QTime, QLoggingCategory, qInstallMessageHandler, qCritical, \
    qWarning
from PySide6.QtWidgets import QMessageBox, QWidget

from src.core.ui_utils import close_splash_screen

_ID_TAG = "[LOGGING_UTILS]"


class LogLevel(StrEnum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    FATAL = "fatal"


_LOG_LEVEL = LogLevel.DEBUG # Default


def setup_logging() -> None:
    # Only reconfigure if the stream exists and supports this method (prevents crash in PyInstaller --windowed EXE)
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    if sys.stderr and hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(line_buffering=True)

    QLoggingCategory.defaultCategory().setEnabled(QtMsgType.QtDebugMsg, True)
    qInstallMessageHandler(_custom_logger)


def _custom_logger(msg_type: QtMsgType, context: str, msg: str) -> None:
    log_map = {
        QtMsgType.QtDebugMsg: (QCoreApplication.translate("logging_utils", "DEBUG"), 0),
        QtMsgType.QtInfoMsg: (QCoreApplication.translate("logging_utils", "INFO"), 1),
        QtMsgType.QtWarningMsg: (QCoreApplication.translate("logging_utils", "WARNING"), 2),
        QtMsgType.QtCriticalMsg: (QCoreApplication.translate("logging_utils", "CRITICAL"), 3),
        QtMsgType.QtFatalMsg: (QCoreApplication.translate("logging_utils", "FATAL"), 4),
    }

    log_label, level = log_map.get(msg_type, (QCoreApplication.translate("logging_utils", "UNKNOWN"), 1))

    threshold = {
        LogLevel.DEBUG: 0,
        LogLevel.INFO: 1,
        LogLevel.WARNING: 2,
        LogLevel.CRITICAL: 3,
        LogLevel.FATAL: 4,
    }.get(_LOG_LEVEL, 1)

    if level >= threshold:
        time_str = QTime.currentTime().toString("HH:mm:ss")
        stream = sys.stderr if level >= 2 else sys.stdout
        stream.write(f"[{time_str}] [{log_label}] {msg}\n")
        stream.flush()


def set_log_level(level: str) -> None:
    global _LOG_LEVEL
    try:
        _LOG_LEVEL = LogLevel(level.lower())
    except Exception as e:
        valid_levels = ", ".join(str(e.value) for e in LogLevel)
        message = QCoreApplication.translate("logging_utils",
                                             "Invalid log level: '{level}'. Must be one of: {valid_levels}. Now use default log level: 'info'.").format(
            level=level, valid_levels=valid_levels)
        qWarning(f"{_ID_TAG} {message}")
        _LOG_LEVEL = LogLevel.INFO


# Custom qFatal, in python don't work like c++ and not print message error before exit
def qFatal(message: str) -> None:
    time_str = QTime.currentTime().toString("HH:mm:ss")
    sys.stderr.write(f"[{time_str}] [FATAL] {message}\n")
    sys.stderr.flush()
    sys.exit(1)


def show_box_critical_and_log(id_tag: str, title: str, message: str, fatal: bool = False,
                              parent: QWidget | None = None) -> None:
    close_splash_screen()

    clean_msg = message.replace("\n", " ").replace("  ", " ").strip()
    if fatal:
        QMessageBox.critical(parent, title, message, QMessageBox.StandardButton.Ok)
        qFatal(f"{id_tag} {clean_msg}")
    else:
        qCritical(f"{id_tag} {clean_msg}")
        QMessageBox.critical(parent, title, message, QMessageBox.StandardButton.Ok)
