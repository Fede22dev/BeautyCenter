from PySide6.QtWidgets import QWidget

from src.ui.generated_ui.clients_page import Ui_clients_page


class ClientsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_clients_page()
        self.ui.setupUi(self)
