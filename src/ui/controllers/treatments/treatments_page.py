from PySide6.QtWidgets import QWidget

from src.ui.generated_ui.treatments_page import Ui_treatments_page


class TreatmentsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_treatments_page()
        self.ui.setupUi(self)
