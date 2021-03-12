import sys
from PySide6.QtWidgets import QApplication
import ui_handler

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = ui_handler.MainWindow()
    window.show()

    sys.exit(app.exec_())