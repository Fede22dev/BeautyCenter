from PySide6.QtCore import QCommandLineParser, QCommandLineOption, QCoreApplication
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.core.logging_utils import show_box_critical_and_log
from src.name_version import APP_NAME, APP_VERSION

_ID_TAG = "[APP_SETUP]"


def setup_app_metadata(app: QApplication) -> None:
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setWindowIcon(QIcon(":/icons/windows_icon"))


def setup_app_args_parser(app: QApplication) -> str | None:
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

    #set_log_level(parser.value(log_level_option)) TODO REACTIVATE FOR FINAL EXE RELEASE

    positional_args = parser.positionalArguments()
    if positional_args:
        title = QCoreApplication.translate("app_setup", "Error")
        message = QCoreApplication.translate("app_setup",
                                             "Unexpected positional argument(s) found:\n{positional_args}.\nUse --help or -h for usage information.").format(
            positional_args=" ".join(positional_args))
        show_box_critical_and_log(_ID_TAG, title, message, True)

    return parser.value(delete_old_option) if parser.isSet(delete_old_option) else None
