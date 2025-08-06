import sys

from PySide6.QtCore import qDebug
from PySide6.QtWidgets import QApplication
from src.resources.generated_qrc import icons_rc  # noqa: F401

from src.core.app_instance import check_another_instance_running, start_local_server
from src.core.app_path_utils import handle_old_exe_deletion, check_exe_path_desktop, check_executable_name
from src.core.app_setups import setup_app_metadata, setup_app_args_parser
from src.core.logging_utils import setup_logging, set_log_level, LogLevel
from src.core.network_utils import check_connection_quality
from src.core.style_and_translation import load_translation, load_style
from src.core.ui_utils import close_splash_screen
from src.core.updater import download_latest_exe_if_exist
from src.name_version import APP_NAME, APP_VERSION
from src.ui.controllers.main.main_window import BeautyCenterMainWindow

_ID_TAG = "[MAIN]"


def main() -> int:
    setup_logging()

    app = QApplication(sys.argv)
    setup_app_metadata(app)

    load_translation(app)

    old_exe_path = setup_app_args_parser(app)

    if getattr(sys, "frozen", False):  # Exe Pyinstaller
        handle_old_exe_deletion(old_exe_path)

        check_executable_name()
        check_exe_path_desktop()

        if check_connection_quality():
            download_latest_exe_if_exist()
    else:
        set_log_level(LogLevel.DEBUG)

    qDebug(f"{_ID_TAG} Start: {APP_NAME} v. {APP_VERSION}")

    # Check if the app is a single instance
    check_another_instance_running()
    start_local_server()

    load_style(app)

    # Load and show UI
    main_window = BeautyCenterMainWindow()

    close_splash_screen()

    main_window.show()
    return app.exec()
