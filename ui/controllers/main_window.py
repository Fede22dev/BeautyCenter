from PySide6.QtWidgets import QMainWindow

from ui.generated_ui.main_window import Ui_beauty_center_main_window


class BeautyCenterMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_beauty_center_main_window()
        self.ui.setupUi(self)

        self.is_menu_expanded = False

    # def _setup_ui(self):
    #     """
    #     Impostazioni iniziali dell'interfaccia dopo il caricamento.
    #     """
    #     # 2. Trova i widget tramite il loro objectName
    #     # Assicurati che questi nomi corrispondano a quelli nel tuo file .ui
    #     self.menu_frame = self.ui.findChild(QWidget, "menu_frame")
    #     self.toggle_button = self.ui.findChild(QWidget, "toggle_button")
    #
    #     # Controlla se i widget sono stati trovati
    #     if not all([self.menu_frame, self.toggle_button]):
    #         raise ValueError("Errore: Uno o più widget non trovati nel file .ui."
    #                          " Controlla gli objectName: 'menu_frame', 'toggle_button'")
    #
    #     # 3. Nascondi il menu all'avvio e imposta la visibilità dei suoi figli
    #     self.ui.menu_frame.setFixedWidth(0)
    #     self._update_menu_children_visibility(False)
    #
    #     # 4. Collega il click del bottone alla funzione (slot)
    #     self.toggle_button.clicked.connect(self.toggle_menu)
    #
    # def _update_menu_children_visibility(self, visible):
    #     """
    #     Mostra o nasconde tutti i widget figli diretti del menu_frame.
    #     Questo evita che siano visibili/interagibili quando il menu è chiuso.
    #     """
    #     for child in self.menu_frame.children():
    #         # Controlliamo se è un widget prima di cambiare la visibilità
    #         if isinstance(child, QWidget):
    #             child.setVisible(visible)
    #
    # @Slot()
    # def toggle_menu(self):
    #     """
    #     Espande o collassa il menu con un'animazione.
    #     """
    #     collapsed_width = 0
    #     expanded_width = 200  # Larghezza del menu desiderata
    #
    #     if self.is_menu_expanded:
    #         # COLLASSA IL MENU
    #         start_width = expanded_width
    #         end_width = collapsed_width
    #         self.is_menu_expanded = False
    #         # Nascondi i widget figli PRIMA di avviare l'animazione di chiusura
    #         self._update_menu_children_visibility(False)
    #     else:
    #         # ESPANDI IL MENU
    #         start_width = collapsed_width
    #         end_width = expanded_width
    #         self.is_menu_expanded = True
    #         # Mostra i widget figli DOPO che l'animazione di apertura è finita
    #         # Lo colleghiamo al segnale finished() dell'animazione
    #
    #     # Crea e configura l'animazione sulla larghezza del frame
    #     self.animation = QPropertyAnimation(self.menu_frame, b"minimumWidth")
    #     self.animation.setDuration(300)
    #     self.animation.setStartValue(start_width)
    #     self.animation.setEndValue(end_width)
    #     self.animation.setEasingCurve(QEasingCurve.InOutQuart)
    #
    #     # Se stiamo espandendo, collega la funzione per mostrare i figli
    #     if self.is_menu_expanded:
    #         self.animation.finished.connect(lambda: self._update_menu_children_visibility(True))
    #
    #     self.animation.start()
    #
    # def show(self):
    #     """Metodo helper per mostrare la finestra principale."""
    #     self.ui.show()
