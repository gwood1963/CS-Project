from message_box import Ui_MessageBox
from game_window import Ui_MainWindow
from PySide6.QtWidgets import QDialog, QMainWindow

class MessageDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MessageBox()
        self.ui.setupUi(self)

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

def displayMessage(msg: str):
    dialog = MessageDialog()
    dialog.ui.message_label.setText(msg)
    dialog.show()
