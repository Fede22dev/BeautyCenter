from PySide6.QtCore import Qt, QDate, QPoint, QEvent
from PySide6.QtWidgets import QWidget, QCalendarWidget, QDialog
from src.ui.generated_ui.appointments_page import Ui_appointments_page

from src.ui.controllers.appointments.appointment_dialog import AppointmentDialog
from src.ui.controllers.appointments.appointments_planner_scene import AppointmentsPlannerScene


class AppointmentsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_appointments_page()
        self.ui.setupUi(self)

        self._setup_calendar_popup()
        self._setup_date_picker()
        self._setup_appointments_planner()

    def _setup_calendar_popup(self):
        self._calendar_popup = QCalendarWidget(self)
        self._calendar_popup.setWindowFlags(Qt.WindowType.Popup)
        self._calendar_popup.setGridVisible(True)
        self._calendar_popup.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self._calendar_popup.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.NoHorizontalHeader)
        self._calendar_popup.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        self._calendar_popup.setMinimumDate(QDate(2025, 8, 1))
        self._calendar_popup.clicked.connect(self._on_calendar_date_selected)

    def _setup_date_picker(self):
        self.ui.select_date_dedit.setDate(QDate.currentDate())

        self.ui.reset_date_tbtn.clicked.connect(lambda: self.ui.select_date_dedit.setDate(QDate.currentDate()))
        self.ui.open_calendar_tbtn.clicked.connect(self._show_calendar_popup)

        self.ui.previous_month_pbtn.clicked.connect(self._change_month(-1))
        self.ui.next_month_pbtn.clicked.connect(self._change_month(+1))
        self.ui.previous_week_pbtn.clicked.connect(self._change_day(-7))
        self.ui.next_week_pbtn.clicked.connect(self._change_day(+7))
        self.ui.previous_day_pbtn.clicked.connect(self._change_day(-1))
        self.ui.next_day_pbtn.clicked.connect(self._change_day(+1))

        self.ui.select_date_dedit.dateChanged.connect(self._load_appointments_for_date)

    def _show_calendar_popup(self):
        if not self._calendar_popup:
            return

        parent_pos = self.ui.select_date_dedit.mapToGlobal(QPoint(0, self.ui.select_date_dedit.height()))
        self._calendar_popup.setSelectedDate(self.ui.select_date_dedit.date())
        self._calendar_popup.move(parent_pos)
        self._calendar_popup.show()

    def _on_calendar_date_selected(self, date: QDate):
        self.ui.select_date_dedit.setDate(date)
        if self._calendar_popup:
            self._calendar_popup.hide()

    def _change_day(self, delta: int):
        def handler():
            date = self.ui.select_date_dedit.date().addDays(delta)
            self.ui.select_date_dedit.setDate(date)

        return handler

    def _change_month(self, delta: int):
        def handler():
            date = self.ui.select_date_dedit.date().addMonths(delta)
            self.ui.select_date_dedit.setDate(date)

        return handler

    def _setup_appointments_planner(self):
        self.scene = AppointmentsPlannerScene()
        self.scene.set_appointment_callbacks(self._on_create_appt, self._on_edit_appt)
        self.ui.planner_grphview.setScene(self.scene)

        example_appointments = [
            {
                "operator": "Anna",
                "start": "08:00",
                "duration": 60,
                "client": "Francesca Rossi",
                "treatment": "Taglio",
                "cabin": 1,
                "notes": "Taglio scalato e shampoo",
            },
            {
                "operator": "Luca",
                "start": "08:30",
                "duration": 90,
                "client": "Luca Bianchi",
                "treatment": "Piega",
                "cabin": 2,
                "notes": "Piega classica",
            },
            {
                "operator": "Anna",
                "start": "09:00",
                "duration": 60,
                "client": "Maria Verdi",
                "treatment": "Colore",
                "cabin": 3,
                "notes": "Colore naturale, coprire ricrescita",
            },
            {
                "operator": "Sofia",
                "start": "10:32",
                "duration": 94,
                "client": "Carla Blu",
                "treatment": "Piega",
                "cabin": 1,
                "notes": "",
            },
            {
                "operator": "Luca",
                "start": "10:17",
                "duration": 77,
                "client": "Elena Grigia",
                "treatment": "Colore",
                "cabin": 2,
                "notes": "",
            }
        ]

        # carica i dati reali o mock se vuoi test
        self.scene.load_appointments(example_appointments)
        self.ui.planner_grphview.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.ui.planner_grphview.viewport() and event.type() == QEvent.Type.Resize:
            view_width = self.ui.planner_grphview.viewport().width()
            self.scene.redraw(view_width=view_width)
        return super().eventFilter(obj, event)

    def _load_appointments_for_date(self):
        self.scene.load_appointments([])

    def _on_create_appt(self, operator, start, cell_item=None):
        dlg = AppointmentDialog(
            self.scene.operators,
            self.scene.clients,
            self.scene.treatments,
            self.scene.cabins,
            data={
                "operator": operator,
                "start": start,
                "duration": 30,
            },
            parent=self
        )

        if cell_item is not None:
            result = self.show_appointment_dialog(dlg, cell_item)
        else:
            result = dlg.exec()

        if result == QDialog.DialogCode.Accepted:
            appt_data = dlg.get_appointment()
            appt_data["cabin_color"] = self.scene.cabins[appt_data["cabin"]][1]
            self.scene.add_or_update_appointment(appt_data)

    def _on_edit_appt(self, item, data, cell_item=None):
        dlg = AppointmentDialog(
            self.scene.operators,
            self.scene.clients,
            self.scene.treatments,
            self.scene.cabins,
            data=data,
            parent=self
        )

        if cell_item is not None:
            result = self.show_appointment_dialog(dlg, cell_item)
        else:
            result = dlg.exec()

        if result == QDialog.DialogCode.Accepted:
            appt_data = dlg.get_appointment()
            appt_data["cabin_color"] = self.scene.cabins[appt_data["cabin"]][1]
            self.scene.add_or_update_appointment(appt_data, item)
        elif result == 2:  # User deleted the appointment
            self.scene.remove_appointment(item)

    def show_appointment_dialog(self, dialog, cell_item):
        # Coordinate rettangolo in scena e globale
        rect = cell_item.boundingRect()
        scene_center = cell_item.mapToScene(rect.center())
        scene_right = cell_item.mapToScene(rect.right(), rect.center().y())
        scene_left = cell_item.mapToScene(rect.left(), rect.center().y())

        # Dimensione dialog (deve essere noto/creata, o forzata)
        dialog_width = dialog.width() if dialog.width() > 0 else 400
        dialog_height = dialog.height() if dialog.height() > 0 else 320

        # Coordinate candidate globali
        pos_right = self.ui.planner_grphview.mapToGlobal(self.ui.planner_grphview.mapFromScene(scene_right))
        pos_left = self.ui.planner_grphview.mapToGlobal(self.ui.planner_grphview.mapFromScene(scene_left))

        # Offset verticale per centrare il dialog sulla cella
        pos_y = pos_right.y() - dialog_height // 2

        # Ottieni dimensioni schermo
        screen = self.ui.planner_grphview.screen().availableGeometry()
        # Preferisci a destra, ma se esce mettilo a sinistra
        if pos_right.x() + dialog_width < screen.right() - 10:
            final_x = pos_right.x()
        else:
            final_x = pos_left.x() - dialog_width
            if final_x < screen.left() + 10:
                final_x = screen.left() + 10  # fallback per schermi stretti
        # Clamp verticale se necessario
        final_y = max(screen.top() + 10, min(pos_y, screen.bottom() - dialog_height - 10))

        dialog.move(final_x, final_y)
        return dialog.exec()
