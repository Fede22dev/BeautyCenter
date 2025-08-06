from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon, QFontMetrics
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QColorDialog, QHeaderView, QTableWidgetItem, QHBoxLayout, \
    QSizePolicy
from src.resources.generated_qrc import icons_rc  # noqa: F401
from src.ui.generated_ui.settings_page import Ui_settings_page


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
