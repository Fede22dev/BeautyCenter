from PySide6.QtCore import Qt, QSize, QTime
from PySide6.QtGui import QFont, QIcon, QFontMetrics
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QColorDialog, QHeaderView, QTableWidgetItem, QHBoxLayout, \
    QSizePolicy
from src.resources.generated_qrc import icons_rc  # noqa: F401
from src.ui.generated_ui.settings_page import Ui_settings_page

from src.databases.local.cruds.cabin import CabinRepository
from src.databases.local.cruds.operator import OperatorRepository
from src.databases.schemes.schemas import Operator, Cabin

_ID_TAG = "[SETTINGS_PAGE]"


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_settings_page()
        self.ui.setupUi(self)

        self.ui.cabins_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ui.operators_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        font = QFont("Segoe UI", 13, QFont.Weight.DemiBold)
        metrics = QFontMetrics(font)
        row_height = metrics.height() + 15
        self.ui.cabins_table.horizontalHeader().setFixedHeight(row_height)
        self.ui.operators_table.horizontalHeader().setFixedHeight(row_height)

        for col in range(self.ui.cabins_table.columnCount()):
            item = self.ui.cabins_table.horizontalHeaderItem(col)
            item.setFont(font)

        for col in range(self.ui.operators_table.columnCount()):
            item = self.ui.operators_table.horizontalHeaderItem(col)
            item.setFont(font)

        self._cabins_color = []
        self._operators_name = []

        self._update_cabins_table()
        self.ui.num_cabins_spinb.valueChanged.connect(self._update_cabins_table)

        self._update_operators_table()
        self.ui.num_operators_spinb.valueChanged.connect(self._update_operators_table)

        self._db_cabins_color = []
        self._db_operators_name = []

        # OperatorRepository.add_or_update_operator(Operator(id=0, name="sarA"))
        # OperatorRepository.add_or_update_operator(Operator(name="VAry"))
        # OperatorRepository.add_or_update_operator(Operator(id=40, name="aaaa"))

        def on_result_cab(cabins: list[Cabin]):
            print(cabins)
            # Aggiorno spinbox in base ai dati DB
            # self.ui.num_cabins_spinb.setValue(len(cabins))
            # self._fill_cabins_table(cabins)  # Popolo con i dati reali

        CabinRepository.get_all_cabins(self, on_result_cab)

        def on_result_ops(operators: list[Operator]):
            print(operators)
            # self.ui.num_operators_spinb.setValue(len(operators))
            # self._fill_operators_table(operators)

        OperatorRepository.get_all_operators(self, on_result_ops)

        self.ui.min_hour_tedit.timeChanged.connect(lambda time: self.ui.min_hour_tedit.setTime(QTime(time.hour(), 0)))
        self.ui.max_hour_tedit.timeChanged.connect(lambda time: self.ui.max_hour_tedit.setTime(QTime(time.hour(), 0)))

    # def _fill_cabins_table(self, cabins: list[Cabin]):
    #     self.ui.cabins_table.setRowCount(0)
    #     self._cabins_color.clear()
    #
    #     for i, cabin in enumerate(cabins):
    #         self._insert_cabin_row(i, cabin.number , cabin.hex_color)  # funzione helper
    #
    # def _fill_operators_table(self, operators: list[Operator]):
    #     self.ui.operators_table.setRowCount(0)
    #     self._operators_name.clear()
    #
    #     for i, operator in enumerate(operators):
    #         self._insert_operator_row(i, operator.name)
    #
    # def _insert_cabin_row(self, i: int, name: int = 0, color: str = None):
    #     # Inserisce una singola riga di cabina (può essere vuota)
    #     self.ui.cabins_table.insertRow(i)
    #
    #     # Nome cabina
    #     item = QTableWidgetItem(name or f"Cabina {i + 1}")
    #     font = QFont("Segoe UI", 11, QFont.Weight.DemiBold)
    #     item.setFont(font)
    #     item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #     item.setFlags(Qt.ItemFlag.ItemIsEnabled)
    #     self.ui.cabins_table.setItem(i, 0, item)
    #
    #     # Bottone colore
    #     picker_button = QPushButton(" Choice color")
    #     font = QFont("Segoe UI", 11)
    #     picker_button.setFont(font)
    #     picker_button.setFlat(True)
    #     picker_button.setIcon(QIcon(":/icons/palette"))
    #     picker_button.setIconSize(QSize(24, 24))
    #     picker_button.setCursor(Qt.CursorShape.PointingHandCursor)
    #     picker_button.setStyleSheet("padding: 6px;")
    #     picker_button.clicked.connect(lambda _, idx=i: self.pick_cabin_color(idx))
    #
    #     picker_container = QWidget()
    #     picker_layout = QHBoxLayout(picker_container)
    #     picker_layout.setContentsMargins(24, 4, 24, 2)
    #     picker_layout.addWidget(picker_button)
    #     picker_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    #     self.ui.cabins_table.setCellWidget(i, 1, picker_container)
    #
    #     # Anteprima colore
    #     preview = QLabel(color.upper() if color else "—")
    #     font = QFont("Segoe UI", 11, QFont.Weight.Medium)
    #     preview.setFont(font)
    #     preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
    #     self.ui.cabins_table.setCellWidget(i, 2, preview)
    #
    #     self._cabins_color.append(color)
    #
    # def _insert_operator_row(self, i: int, name: str = ""):
    #     self.ui.operators_table.insertRow(i)
    #
    #     # Numero
    #     item = QTableWidgetItem(str(i + 1))
    #     font = QFont("Segoe UI", 11, QFont.Weight.DemiBold)
    #     item.setFont(font)
    #     item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #     item.setFlags(Qt.ItemFlag.ItemIsEnabled)
    #     self.ui.operators_table.setItem(i, 0, item)
    #
    #     # Nome operatore
    #     name_item = QTableWidgetItem(name)
    #     name_item.setFont(font)
    #     name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #     self.ui.operators_table.setItem(i, 1, name_item)
    #
    #     self._operators_name.append(name or None)
    #
    # def _update_cabins_table(self):
    #     target_rows = self.ui.num_cabins_spinb.value()
    #     current_rows = self.ui.cabins_table.rowCount()
    #
    #     if target_rows > current_rows:  # Aggiungi righe vuote
    #         for i in range(current_rows, target_rows):
    #             self._insert_cabin_row(i)
    #     elif target_rows < current_rows:  # Rimuovi righe
    #         for i in reversed(range(target_rows, current_rows)):
    #             self.ui.cabins_table.removeRow(i)
    #             self._cabins_color.pop()
    #
    # def _update_operators_table(self):
    #     target_rows = self.ui.num_operators_spinb.value()
    #     current_rows = self.ui.operators_table.rowCount()
    #
    #     if target_rows > current_rows:  # Aggiungi righe vuote
    #         for i in range(current_rows, target_rows):
    #             self._insert_operator_row(i)
    #     elif target_rows < current_rows:  # Rimuovi righe
    #         for i in reversed(range(target_rows, current_rows)):
    #             self.ui.operators_table.removeRow(i)
    #             self._operators_name.pop()

    def _update_cabins_table(self):
        cabins_num = self.ui.num_cabins_spinb.value()
        current_rows = self.ui.cabins_table.rowCount()

        # Add rows
        if cabins_num > current_rows:
            for i in range(current_rows, cabins_num):
                self.ui.cabins_table.insertRow(i)

                # Column 1: cabin name
                item = QTableWidgetItem(f"{i + 1}")
                font = QFont("Segoe UI", 11, QFont.Weight.DemiBold)
                item.setFont(font)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.ui.cabins_table.setItem(i, 0, item)

                # Column 2: color picker
                picker_button = QPushButton(" Choice color")
                font = QFont("Segoe UI", 11)
                picker_button.setFont(font)
                picker_button.setFlat(True)
                picker_button.setIcon(QIcon(":/icons/palette"))
                picker_button.setIconSize(QSize(24, 24))
                picker_button.setCursor(Qt.CursorShape.PointingHandCursor)
                picker_button.setStyleSheet("padding: 6px;")
                picker_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                picker_button.clicked.connect(lambda checked=False, idx=i: self.pick_cabin_color(idx))

                picker_container = QWidget()
                picker_layout = QHBoxLayout(picker_container)
                picker_layout.setContentsMargins(24, 4, 24, 2)  # left, top, right, bottom
                picker_layout.addWidget(picker_button)
                picker_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.ui.cabins_table.setCellWidget(i, 1, picker_container)

                # Column 3: color
                preview = QLabel("—")
                font = QFont("Segoe UI", 11, QFont.Weight.Medium)
                preview.setFont(font)
                preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.ui.cabins_table.setCellWidget(i, 2, preview)

                picker_container.adjustSize()
                preview.adjustSize()

                row_height = max(picker_container.sizeHint().height(), preview.sizeHint().height()) + 4
                self.ui.cabins_table.setRowHeight(i, row_height)

                self._cabins_color.append(None)
        elif cabins_num < current_rows:  # Remove row
            for i in reversed(range(cabins_num, current_rows)):
                self.ui.cabins_table.removeRow(i)
                self._cabins_color.pop()

    def pick_cabin_color(self, idx: int):
        color = QColorDialog.getColor(parent=self, title=f"Seleziona colore per Cabina {idx + 1}")
        if color.isValid():
            self._cabins_color[idx] = color

            # Update preview column 3
            preview: QLabel = self.ui.cabins_table.cellWidget(idx, 2)
            preview.setText(color.name().upper())

            r, g, b = color.red(), color.green(), color.blue()
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            text_color = "#000000" if luminance > 128 else "#FFFFFF"

            preview.setStyleSheet(
                f"background-color: {color.name()}; color: {text_color}; border: 1px solid #555; padding: 4px;")

    def _update_operators_table(self):
        operators_num = self.ui.num_operators_spinb.value()
        current_rows = self.ui.operators_table.rowCount()

        # Add rows
        if operators_num > current_rows:
            for i in range(current_rows, operators_num):
                self.ui.operators_table.insertRow(i)

                # Column 1: operator number
                item = QTableWidgetItem(f"{i + 1}")
                font = QFont("Segoe UI", 11, QFont.Weight.DemiBold)
                item.setFont(font)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.ui.operators_table.setItem(i, 0, item)

                # Column 2: operator name
                item = QTableWidgetItem()
                item.setFont(font)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.ui.operators_table.setItem(i, 1, item)

                metrics = QFontMetrics(font)
                row_height = metrics.height() + 15
                self.ui.operators_table.setRowHeight(i, row_height)

                self._operators_name.append(None)
        elif operators_num < current_rows:  # Remove row
            for i in reversed(range(operators_num, current_rows)):
                self.ui.operators_table.removeRow(i)
                self._operators_name.pop()
