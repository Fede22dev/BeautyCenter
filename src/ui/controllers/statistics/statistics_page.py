from PySide6.QtWidgets import QWidget

from src.ui.generated_ui.statistics_page import Ui_statistics_page


class StatisticsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_statistics_page()
        self.ui.setupUi(self)
