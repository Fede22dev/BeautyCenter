import os
import sys

from PySide6.QtCore import QTime


# Get an absolute path to resource (compatible with PyInstaller)
def get_resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Custom qFatal, in python don't work like c++ and not print message error before exit
def qFatal(message: str):
    time_str = QTime.currentTime().toString("HH:mm:ss")
    output_stream = sys.stderr
    output_stream.write(f"[{time_str}] [FATAL] {message}\n")
    output_stream.flush()
    sys.exit(1)
