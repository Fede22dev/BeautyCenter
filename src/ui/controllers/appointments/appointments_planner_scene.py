from PySide6.QtCore import Qt, QRectF, QTime
from PySide6.QtGui import QBrush, QColor, QPen, QFont
from PySide6.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsSimpleTextItem, QGraphicsItem

DEFAULT_OPERATORS = ["Anna", "Luca", "Sofia"]
DEFAULT_CABINS = {
    1: ("Cabina 1", QColor("#EF5350")),
    2: ("Cabina 2", QColor("#66BB6A")),
    3: ("Cabina 3", QColor("#42A5F5")),
}
DEFAULT_TREATMENTS = ["Taglio", "Piega", "Colore"]
DEFAULT_CLIENTS = ["Francesca Rossi", "Luca Bianchi", "Maria Verdi"]


def get_time_slots(start: str, end: str, step: int = 1) -> list[str]:
    times = []
    cur = QTime.fromString(start, "HH:mm")
    end_t = QTime.fromString(end, "HH:mm")
    while cur <= end_t:
        times.append(cur.toString("HH:mm"))
        cur = cur.addSecs(step * 60)
    return times


class GridCellItem(QGraphicsRectItem):
    def __init__(self, rect: QRectF, col: int, row: int, operator: str, slot: str, on_click):
        super().__init__(rect)
        self.setPen(QPen(QColor("#505050")))
        self.setBrush(QColor("#3C3C3E"))
        self.col = col
        self.row = row
        self.operator = operator
        self.slot = slot
        self.on_click = on_click
        self.setAcceptHoverEvents(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.on_click:
            self.on_click(self.operator, self.slot, self)

    def hoverEnterEvent(self, event):
        self.setBrush(QColor("#505050"))

    def hoverLeaveEvent(self, event):
        self.setBrush(QColor("#3C3C3E"))


class AppointmentItem(QGraphicsRectItem):
    def __init__(self, rect: QRectF, data, on_edit):
        super().__init__(rect)
        self.data = data
        self.on_edit = on_edit
        self.setBrush(DEFAULT_CABINS.get(data["cabin"], ("undefined", QColor("#888888")))[1])
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        font = QFont()
        font.setPointSize(11)
        font.setWeight(QFont.Weight.Bold)
        label = f"{data["client"]} ({data["treatment"]})"
        self.text_item = QGraphicsSimpleTextItem(label, self)
        self.text_item.setFont(font)
        self.text_item.setBrush(QColor("#FFFFFF"))
        self.text_item.setPos(rect.left() + 7, rect.top() + 7)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.on_edit:
            self.on_edit(self, self.data, self)


class AppointmentsPlannerScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.operators = list(DEFAULT_OPERATORS)
        self.cabins = dict(DEFAULT_CABINS)
        self.treatments = list(DEFAULT_TREATMENTS)
        self.clients = list(DEFAULT_CLIENTS)
        self.work_start = "07:00"
        self.work_end = "22:00"
        self.slot_minutes = 30
        self.grid_left = 80
        self.header_height = 44
        self.cell_width_min = 110
        self.cell_height = 42
        self.appointments = []
        self.grid = {}
        self._on_appointment_create = None
        self._on_appointment_edit = None

    def set_appointment_callbacks(self, create_fn, edit_fn):
        self._on_appointment_create = create_fn
        self._on_appointment_edit = edit_fn

    def load_appointments(self, appointments):
        self.appointments = [dict(a) for a in appointments]
        self.redraw()

    def add_or_update_appointment(self, data, item=None):
        if item:
            self.appointments = [
                a for a in self.appointments
                if not (a["start"] == item.data["start"] and a["operator"] == item.data["operator"] and a["client"] ==
                        item.data["client"])
            ]
        self.appointments.append(data)
        self.redraw()

    def remove_appointment(self, item):
        rem = None
        for a in self.appointments:
            if (
                    a["start"] == item.data["start"]
                    and a["operator"] == item.data["operator"]
                    and a["client"] == item.data["client"]
            ):
                rem = a
                break
        if rem:
            self.appointments.remove(rem)
            self.redraw()

    def redraw(self, view_width: int = None):
        self.clear()
        times_slot = get_time_slots(self.work_start, self.work_end, self.slot_minutes)
        num_rows = len(times_slot)
        num_cols = len(self.operators)

        # Determine actual view width (responsive on resize)
        view = self.views()[0] if self.views() else None
        if view_width is not None:
            actual_view_width = view_width
        elif view:
            actual_view_width = view.viewport().width()
        else:
            actual_view_width = self.grid_left + self.cell_width_min * num_cols

        # Adaptive column width - but don't go smaller than the minimum
        cell_width = max(self.cell_width_min, (actual_view_width - self.grid_left) // max(1, num_cols))

        # If the grid needs more space than what's available, allow horizontal scrolling
        total_grid_width = self.grid_left + cell_width * num_cols
        if total_grid_width < self.grid_left + self.cell_width_min * num_cols:
            cell_width = self.cell_width_min
            total_grid_width = self.grid_left + cell_width * num_cols

        total_grid_height = self.header_height + self.cell_height * num_rows
        self.setSceneRect(QRectF(18, 0, total_grid_width, total_grid_height))

        # Draw the left time column (centered)
        font_label = QFont("Segoe UI", 12, QFont.Weight.Bold)
        for i, t in enumerate(times_slot):
            y = self.header_height + i * self.cell_height
            self.addRect(0, y, self.grid_left, self.cell_height, QPen(QColor("#39394A")), QBrush(QColor("#252526")))
            label = QGraphicsSimpleTextItem(t)
            label.setFont(font_label)
            label.setBrush(QColor("#BFBFBF"))
            # Center text horizontally and vertically in grid_left/self.cell_h
            br = label.boundingRect()
            cx = (self.grid_left - br.width()) / 2
            cy = y + (self.cell_height - br.height()) / 2
            label.setPos(cx, cy)
            self.addItem(label)

        # Draw top operator headers (centered)
        font_header = QFont("Segoe UI", 18, QFont.Weight.Bold)
        for j, op in enumerate(self.operators):
            x = self.grid_left + j * cell_width
            self.addRect(x, 0, cell_width, self.header_height, QPen(QColor("#505050")), QBrush(QColor("#2D2D30")))
            ht = QGraphicsSimpleTextItem(op)
            ht.setFont(font_header)
            ht.setBrush(QColor("#FF4081"))
            # Center text horizontally and vertically in cell_width/self.header_height
            br = ht.boundingRect()
            cx = x + (cell_width - br.width()) / 2
            cy = (self.header_height - br.height()) / 2
            ht.setPos(cx, cy)
            self.addItem(ht)

        # Draw interactive grid cells
        self.grid = {}
        for i, slot in enumerate(times_slot):
            for j, op in enumerate(self.operators):
                x = self.grid_left + j * cell_width
                y = self.header_height + i * self.cell_height
                rect = QRectF(x, y, cell_width, self.cell_height)
                cell = GridCellItem(rect, j, i, op, slot, self._on_appointment_create)
                self.addItem(cell)
                self.grid[(j, i)] = cell

        # Draw appointments
        for appointment in self.appointments:
            if appointment["operator"] in self.operators:
                col = self.operators.index(appointment["operator"])

                start_time = QTime.fromString(self.work_start, "HH:mm")
                apt_time = QTime.fromString(appointment["start"], "HH:mm")
                if not apt_time.isValid():
                    continue  # skip invalid times

                minutes_from_start = start_time.secsTo(apt_time) // 60
                y = self.header_height + minutes_from_start * (self.cell_height / self.slot_minutes)

                span = max(1, appointment["duration"] // self.slot_minutes)
                h = span * self.cell_height
                x = self.grid_left + col * cell_width

                data = dict(appointment)
                item = AppointmentItem(QRectF(x + 2, y + 2, cell_width - 4, h - 4), data, self._on_appointment_edit)
                self.addItem(item)
