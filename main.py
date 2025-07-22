from PySide6.QtCore import QFile, QIODeviceBase
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication([])
    loader = QUiLoader()
    ui_file = QFile("ui/main_window/main_window.ui")
    ui_file.open(QIODeviceBase.OpenModeFlag.ReadOnly)
    window = loader.load(ui_file)
    ui_file.close()

    window.show()
    app.exec()
