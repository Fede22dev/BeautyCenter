import getpass

from PySide6.QtCore import QCoreApplication
from PySide6.QtNetwork import QLocalServer, QLocalSocket

from src.core.logging_utils import show_box_critical_and_log
from src.name_version import APP_NAME

_ID_TAG = "[APP_INSTANCE]"

_SERVER_NAME = f"{APP_NAME}_instance_{getpass.getuser()}"
_instance_server = None


def check_another_instance_running() -> None:
    socket = QLocalSocket()
    socket.connectToServer(_SERVER_NAME)
    if socket.waitForConnected(500):
        socket.abort()
        socket.deleteLater()

        title = QCoreApplication.translate("app_instance", "Error")
        message = QCoreApplication.translate("app_instance",
                                             "Another instance of {app_name} is already running.").format(
            app_name=APP_NAME)
        show_box_critical_and_log(_ID_TAG, title, message, True)


def start_local_server() -> None:
    # Try to listen, if address busy try to remove the server and retry once
    global _instance_server
    _instance_server = QLocalServer()
    if not _instance_server.listen(_SERVER_NAME):
        QLocalServer.removeServer(_SERVER_NAME)
        if not _instance_server.listen(_SERVER_NAME):
            title = QCoreApplication.translate("app_instance", "Error")
            message = QCoreApplication.translate("app_instance",
                                                 "Failed to start local server:\n{instance_server_name}\nError: {error}").format(
                instance_server_name=_SERVER_NAME, error=_instance_server.errorString())
            show_box_critical_and_log(_ID_TAG, title, message, True)
