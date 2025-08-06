from PySide6.QtCore import QTime
from PySide6.QtWidgets import QDialog, QMessageBox

from src.ui.generated_ui.appointment_dialog import Ui_appointment_dialog


class AppointmentDialog(QDialog):
    def __init__(self, operators, clients, treatments, cabins, data=None, parent=None):
        super().__init__(parent)
        self.ui = Ui_appointment_dialog()
        self.ui.setupUi(self)

        # Prepare combobox values
        self.ui.operators_ckb.addItems(operators)
        self.ui.clients_ckb.addItems(clients)
        self.ui.treatments_ckb.addItems(treatments)
        for c_id, (cab_name, _) in cabins.items():
            self.ui.cabins_ckb.addItem(cab_name, c_id)

        # Populate fields in edit mode
        if data:
            self.ui.operators_ckb.setCurrentText(data.get("operator", ""))
            self.ui.start_tedit.setTime(QTime.fromString(data.get("start", ""), "HH:mm"))
            self.ui.duration_spinb.setValue(data.get("duration", 30))
            self.ui.clients_ckb.setCurrentText(data.get("client", ""))
            self.ui.treatments_ckb.setCurrentText(data.get("treatment", ""))
            idx = self.ui.cabins_ckb.findData(data.get("cabin", 1))
            if idx >= 0:
                self.ui.cabins_ckb.setCurrentIndex(idx)
            self.ui.notes_txtedit.setText(data.get("notes", ""))
            self.ui.delete_pbtn.setVisible(True)
        else:
            self.ui.delete_pbtn.setVisible(False)

        # Connect buttons
        self.ui.save_pbtn.clicked.connect(self.accept)
        self.ui.cancel_pbtn.clicked.connect(self.reject)
        self.ui.delete_pbtn.clicked.connect(self._request_delete)

    def get_appointment(self):
        return {
            "operator": self.ui.operators_ckb.currentText(),
            "start": self.ui.start_tedit.time().toString("HH:mm"),
            "duration": self.ui.duration_spinb.value(),
            "client": self.ui.client_ckb.currentText(),
            "treatment": self.ui.treatments_ckb.currentText(),
            "cabin": self.ui.cabins_ckb.currentData(),
            "notes": self.ui.notes_txtedit.toPlainText()
        }

    def _request_delete(self):
        self.done(2)  # Return special code for DELETE

    def accept(self):
        # Data validation
        if not self.ui.operators_ckb.currentText() or not self.ui.start_tedit.time() or not self.ui.clients_ckb.currentText() or not self.ui.treatments_ckb.currentText():
            QMessageBox.warning(self, "Validation", "Fill all required fields.")
            return

        super().accept()
