import sys

from PySide6.QtCore import QTime, QDir, QStandardPaths


# Get an absolute path to resource (compatible with PyInstaller)
def get_resource_path(relative_path: str) -> str:
    base_path = getattr(sys, '_MEIPASS', QDir.currentPath())
    return QDir(base_path).filePath(relative_path)


def get_desktop_path() -> str:
    desktop = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
    if not desktop:
        home = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation)
        desktop = QDir(home).filePath("Desktop")

    return QDir.toNativeSeparators(desktop)

# Custom qFatal, in python don't work like c++ and not print message error before exit
def qFatal(message: str):
    time_str = QTime.currentTime().toString("HH:mm:ss")
    sys.stderr.write(f"[{time_str}] [FATAL] {message}\n")
    sys.stderr.flush()
    sys.exit(1)
