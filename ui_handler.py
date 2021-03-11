from message_box import Ui_MessageBox
from PySide6.QtWidgets import QDialog

class MessageDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MessageBox()
        self.ui.setupUi(self)

def displayMessage(msg: str):
    dialog = MessageDialog()
    dialog.ui.message_label.setText(msg)
    dialog.show()
