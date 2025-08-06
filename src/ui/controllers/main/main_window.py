from enum import IntEnum

from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QPushButton
from src.resources.generated_qrc import icons_rc  # noqa: F401
from src.ui.generated_ui.main_window import Ui_beauty_center_main_window

from src.ui.controllers.appointments.appointments_page import AppointmentsPage
from src.ui.controllers.clients.clients_page import ClientsPage
from src.ui.controllers.settings.settings_page import SettingsPage
from src.ui.controllers.statistics.statistics_page import StatisticsPage
from src.ui.controllers.treatments.treatments_page import TreatmentsPage


class PageIndex(IntEnum):
    APPOINTMENTS = 0
    CLIENTS = 1
    STATISTICS = 2
    TREATMENTS = 3
    SETTINGS = 4


class BeautyCenterMainWindow(QMainWindow):
    ANIMATION_DURATION = 300

    def __init__(self):
        super().__init__()

        self.ui = Ui_beauty_center_main_window()
        self.ui.setupUi(self)

        self._setup_sidebar()
        self._setup_stacked_pages()

    def _setup_sidebar(self) -> None:
        self._is_sidebar_expanded = False
        self.sidebar_collapsed_width = self.ui.sidebar_frame.minimumWidth()
        self.sidebar_expanded_width = self.ui.sidebar_frame.maximumWidth()

        self._sidebar_buttons = [btn for btn in self.ui.sidebar_frame.findChildren(QPushButton) if
                                 btn is not self.ui.exp_col_sidebar_pbtn]

        # Sidebar width animation setup
        self._sidebar_animation = QPropertyAnimation(self.ui.sidebar_frame, b"minimumWidth")
        self._sidebar_animation.setDuration(self.ANIMATION_DURATION)
        self._sidebar_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._sidebar_animation.finished.connect(self._on_animation_finished)
        self.ui.exp_col_sidebar_pbtn.clicked.connect(self._toggle_sidebar)

        self.ui.appointments_page_pbtn.clicked.connect(
            lambda: self.ui.stacked_widget.setCurrentIndex(PageIndex.APPOINTMENTS))
        self.ui.clients_page_pbtn.clicked.connect(lambda: self.ui.stacked_widget.setCurrentIndex(PageIndex.CLIENTS))
        self.ui.statistics_page_pbtn.clicked.connect(
            lambda: self.ui.stacked_widget.setCurrentIndex(PageIndex.STATISTICS))
        self.ui.treatments_page_pbtn.clicked.connect(
            lambda: self.ui.stacked_widget.setCurrentIndex(PageIndex.TREATMENTS))
        self.ui.settings_page_pbtn.clicked.connect(lambda: self.ui.stacked_widget.setCurrentIndex(PageIndex.SETTINGS))

    def _setup_stacked_pages(self) -> None:
        self.ui.stacked_widget.addWidget(AppointmentsPage())
        self.ui.stacked_widget.addWidget(ClientsPage())
        self.ui.stacked_widget.addWidget(StatisticsPage())
        self.ui.stacked_widget.addWidget(TreatmentsPage())
        self.ui.stacked_widget.addWidget(SettingsPage())

    def _on_animation_finished(self) -> None:
        if self._is_sidebar_expanded:
            self._update_sidebar_ui()

    def _toggle_sidebar(self) -> None:
        current_width = self.ui.sidebar_frame.width()
        target_width = self.sidebar_collapsed_width if self._is_sidebar_expanded else self.sidebar_expanded_width

        self._sidebar_animation.stop()
        self._sidebar_animation.setStartValue(current_width)
        self._sidebar_animation.setEndValue(target_width)
        self._sidebar_animation.start()

        self._is_sidebar_expanded = not self._is_sidebar_expanded
        if not self._is_sidebar_expanded:
            self._update_sidebar_ui()

    def _update_sidebar_ui(self) -> None:
        icon = ":/icons/menu_close" if self._is_sidebar_expanded else ":/icons/menu_open"
        self.ui.exp_col_sidebar_pbtn.setIcon(QIcon(icon))

        for btn in self._sidebar_buttons:
            full_text = btn.property("fullText") or ""
            btn.setText(full_text if self._is_sidebar_expanded else "")
