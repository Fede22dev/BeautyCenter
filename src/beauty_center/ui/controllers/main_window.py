from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QPushButton

from resources.generated_qrc import icons_rc  # noqa: F401
from ui.generated_ui.main_window import Ui_beauty_center_main_window  # noqa: F401


class BeautyCenterMainWindow(QMainWindow):
    ANIMATION_DURATION = 300

    def __init__(self):
        super().__init__()

        self.ui = Ui_beauty_center_main_window()
        self.ui.setupUi(self)

        self.sidebar_expanded = False
        self.sidebar_collapsed_width = self.ui.sidebar.minimumWidth()
        self.sidebar_expanded_width = self.ui.sidebar.maximumWidth()

        self.sidebar_buttons = [btn for btn in self.ui.sidebar.findChildren(QPushButton) if
                                btn is not self.ui.exp_col_sidebar_pb]

        # Sidebar width animation setup
        self.sidebar_animation = QPropertyAnimation(self.ui.sidebar, b"minimumWidth")
        self.sidebar_animation.setDuration(self.ANIMATION_DURATION)
        self.sidebar_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.sidebar_animation.finished.connect(self._on_animation_finished)

        self.ui.exp_col_sidebar_pb.clicked.connect(self._toggle_sidebar)

    def _on_animation_finished(self):
        if self.sidebar_expanded:
            self._update_sidebar_ui()

    def _toggle_sidebar(self):
        current_width = self.ui.sidebar.width()
        target_width = self.sidebar_collapsed_width if self.sidebar_expanded else self.sidebar_expanded_width

        self.sidebar_animation.stop()
        self.sidebar_animation.setStartValue(current_width)
        self.sidebar_animation.setEndValue(target_width)
        self.sidebar_animation.start()

        self.sidebar_expanded = not self.sidebar_expanded
        if not self.sidebar_expanded:
            self._update_sidebar_ui()

    def _update_sidebar_ui(self):
        icon = ":/icons/menu_close" if self.sidebar_expanded else ":/icons/menu_open"
        self.ui.exp_col_sidebar_pb.setIcon(QIcon(icon))

        for btn in self.sidebar_buttons:
            full_text = btn.property("fullText") or ""
            btn.setText(full_text if self.sidebar_expanded else "")
