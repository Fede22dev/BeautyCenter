from PySide6.QtCore import QLocale, QTranslator, qDebug, qWarning, QCoreApplication, QFile, QIODeviceBase, QTextStream
from PySide6.QtWidgets import QApplication
from src.resources.generated_qrc import styles_rc  # noqa: F401

from src.core.app_path_utils import _get_resource_path

_ID_TAG = "[STYLE_AND_TRANSLATION]"


def load_translation(app: QApplication) -> None:
    locale = QLocale.system()
    if locale.language() == QLocale.Language.Italian:
        translator = QTranslator()
        if translator.load(_get_resource_path("translations/generated_qm/it.qm")):
            app.installTranslator(translator)
            # qDebug(f"{_ID_TAG} System locale: {locale.name()}")
        else:
            message = QCoreApplication.translate("style_and_translation",
                                                 "Italian translation not found. Use default English translation.")
            qWarning(f"{_ID_TAG} {message}")


def load_style(app: QApplication) -> None:
    file = QFile(":/styles/modern_pink")
    if not file.open(QIODeviceBase.OpenModeFlag.ReadOnly):
        message = QCoreApplication.translate("style_and_translation", "Failed to load style {file_name}").format(
            file_name=file.fileName())
        qWarning(f"{_ID_TAG} {message}")
        return

    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())
    qDebug(f"{_ID_TAG} Loaded style {file.fileName()}.")
