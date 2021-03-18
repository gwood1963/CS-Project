from __future__ import annotations

import typing

from PySide6.QtCore import QByteArray, QMargins, QMimeData, Qt
from PySide6.QtGui import (QBrush, QColor, QDrag, QDragEnterEvent,
                           QDragMoveEvent, QDropEvent, QMouseEvent, QPixmap)
from PySide6.QtWidgets import (QDialog, QFrame, QHBoxLayout, QLabel,
                               QMainWindow, QPushButton, QTableWidgetItem)

import game
from game_window import Ui_MainWindow
from go_to_move import Ui_go_to_move
from input_error import InputError
from message_box import Ui_MessageBox
from new_game_window import Ui_new_game_dialog


class GoToMoveDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_go_to_move()
        self.ui.setupUi(self)
        self.ui.buttonBox.accepted.connect(self.goToMove)

    def goToMove(self):
        main: MainWindow = self.parent()
        move_num = int(self.ui.move_num.text())
        color = 'white' if self.ui.white.isChecked() else 'black'
        main.goToMove(move_num, color)
        self.accept()

class PieceLabel(QLabel):
    def __init__(self, type: typing.Literal['', 'N', 'B', 'R', 'Q', 'K'],
                 color: typing.Literal['black', 'white']):
        self.type = type
        self.color = color
        super().__init__('')
        type_code = type.lower() if type != '' else 'p'
        color_code = 'l' if color == 'white' else 'd'
        self.setPixmap(QPixmap(u":/pieces/images/Chess_"
                               + type_code + color_code + u"t60.png"))
        self.setScaledContents(True)
        self.setFixedSize(60, 60)

class MessageDialog(QDialog):
    def __init__(self, msg: str):
        super().__init__()
        self.ui = Ui_MessageBox()
        self.ui.setupUi(self)
        self.ui.message_label.setText(msg)

class PromotionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setLayout(QHBoxLayout(self))
        for code in ('N', 'B', 'R', 'Q'):
            btn = QPushButton(code)
            btn.setMaximumSize(24, 24)
            btn.setMinimumSize(24,24)
            btn.clicked.connect(self.returnType)
            self.layout().addWidget(btn)

    def returnType(self):
        self.parent().promote_type = self.sender().text()
        self.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.game: game.Game
        self.ui.new_game_btn.clicked.connect(self.startup)
        self.ui.done_btn.clicked.connect(self.setupComplete)
        self.ui.rollback_btn.clicked.connect(self.rollBack)
        self.ui.rollforward_btn.clicked.connect(self.rollForward)
        self.ui.goto_btn.clicked.connect(self.openGoToDialog)
        for frame in self.ui.board.children():
            if isinstance(frame, QFrame) and not isinstance(frame, QLabel):
                layout = QHBoxLayout(frame)
                layout.setContentsMargins(QMargins(0,0,0,0))
                layout.setSpacing(0)
                frame.setLayout(layout)

        self.promote_type: typing.Literal['N', 'B', 'R', 'Q']

        piece_types = ('', 'N', 'B', 'R', 'Q', 'K')
        colors = ('white', 'black')
        for i in range(6):
            for j in range(2):
                label = PieceLabel(piece_types[i], colors[j])
                self.ui.piece_container.layout().addWidget(label, i, j)
                
        def dragFromDock(event: QMouseEvent):
            if event.button() != Qt.LeftButton:
                return

            pos = event.pos()

            if (self.ui.piece_container.geometry().contains(pos)):
                label = self.ui.piece_container.childAt(pos)
                if not isinstance(label, PieceLabel):
                    return
                drag = QDrag(self)
                mime_data = QMimeData()
                pixmap = label.pixmap()
                mime_data.setText(label.color + '_' + label.type)
                mime_data.setData('addPiece', QByteArray())
                
                drag.setMimeData(mime_data)
                drag.setPixmap(pixmap)
                drag.setHotSpot(pos - label.pos())
                dropAction = drag.exec_(Qt.CopyAction)
        self.ui.piece_container.mousePressEvent = dragFromDock

        def dragFromBoard(event: QMouseEvent):
            if event.button() != Qt.LeftButton:
                return

            pos = event.pos()

            if (self.ui.board.geometry().contains(pos)):
                label = self.ui.board.childAt(pos)
                if not isinstance(label, PieceLabel):
                    return
                square = label.parent()
                drag = QDrag(self)
                mime_data = QMimeData()
                pixmap = label.pixmap()
                mime_data.setText(self.square(square))
                mime_data.setData('movePiece', QByteArray())
                
                drag.setMimeData(mime_data)
                drag.setPixmap(pixmap)
                drag.setHotSpot(pos - label.parent().pos())
                dropAction = drag.exec_(Qt.MoveAction)
        self.ui.board.mousePressEvent = dragFromBoard

        def dragEnter(event: QDragEnterEvent):
            if event.mimeData().hasFormat('addPiece') or event.mimeData().hasFormat('movePiece'):
                if event.source() in (self.ui.piece_container, self.ui.board):
                    event.setDropAction(Qt.CopyAction)
                    event.accept()
                else:
                    event.acceptProposedAction()
            else:
                event.ignore()
        self.ui.board.dragEnterEvent = dragEnter

        def dragMove(event: QDragMoveEvent):
            if event.mimeData().hasFormat('addPiece') or event.mimeData().hasFormat('movePiece'):
                if event.source() in (self.ui.piece_container, self.ui.board):
                    event.setDropAction(Qt.CopyAction)
                    event.accept()
                else:
                    event.acceptProposedAction()
            else:
                event.ignore()
        self.ui.board.dragMoveEvent = dragMove

        def dragToBoard(event: QDropEvent):
            pos = event.pos()

            square: QFrame
            for frame in self.ui.board.children():
                if isinstance(frame, QFrame) and frame.geometry().contains(pos):
                    square = frame
                    break
            else:
                event.ignore()
                return

            if event.mimeData().hasFormat('addPiece'):
                mime_data = event.mimeData()
                text = mime_data.text()
                color, type = text.split('_')

                label = PieceLabel(type, color)
                label.move(square.x(), square.y())
                square.layout().addWidget(label)
                label.show()

                self.game.board.addPiece(type, self.square(square), color)

                if event.source() == self.ui.piece_container:
                    event.setDropAction(Qt.CopyAction)
                    event.accept()
                else:
                    event.acceptProposedAction()
            elif event.mimeData().hasFormat('movePiece'):
                mime_data = event.mimeData()
                start = mime_data.text()
                end = self.square(square)

                if self.ui.view_modes.currentWidget() == self.ui.piece_dock:
                    self.game.board.move(start, end)
                    self.updateBoard()

                    if event.source() == self.ui.board:
                        event.setDropAction(Qt.MoveAction)
                        event.accept()
                    else:
                        event.acceptProposedAction()
                else:
                    try:
                        self.game.move(start, end)
                    except InputError as msg:
                        self.displayMessage(msg.msg)
                        event.ignore()
                    else:
                        move = self.game.move_history[-1]
                        if move.checkmate:
                            self.displayMessage('Checkmate.')
                        elif move.check:
                            self.displayMessage('Check.')

                        self.updateBoard()

                        self.addMoveHistory(str(move), move.color)

                        if event.source() == self.ui.board:
                            event.setDropAction(Qt.MoveAction)
                            event.accept()
                        else:
                            event.acceptProposedAction()
            else:
                event.ignore()
        self.ui.board.dropEvent = dragToBoard

    def startup(self):
        new = NewGameWindow()
        new.setParent(self, Qt.Dialog)
        new.exec_()

    def openGoToDialog(self):
        goto = GoToMoveDialog()
        goto.setParent(self, Qt.Dialog)
        goto.exec_()

    def setupComplete(self):
        self.ui.view_modes.setCurrentWidget(self.ui.control_panel)

    def getPromoteType(self) -> typing.Literal['N', 'B', 'R', 'Q']:
        promote_dialog = PromotionDialog()
        promote_dialog.setParent(self, Qt.Dialog)
        promote_dialog.exec_()
        return self.promote_type

    def addMoveHistory(self, move: str, color: typing.Literal['black', 'white']):
        move_entry = QTableWidgetItem(move)
        move_num = self.game.move_number
        rows = self.ui.move_history.rowCount()
        if move_num < self.moveCount():
            self.ui.move_history.clear()
            self.ui.move_history.setRowCount(0)
            for mv in self.game.move_history:
                self.addMoveHistory(str(mv), color)
            return
        if color == 'white' and move_num != 1:
            self.ui.move_history.insertRow(rows)
            rows += 1
        col = 0 if color == 'white' else 1
        move_entry.setTextAlignment(Qt.AlignCenter)
        self.ui.move_history.setItem(rows-1, col, move_entry)

    def moveAt(self, current: int) -> tuple[int, int]:
        if self.ui.move_history.item(0,0):
            return divmod(current-1, 2)
        else:
            return divmod(current, 2)

    def moveCount(self) -> int:
        rows = self.ui.move_history.rowCount()
        count = rows * 2
        if not self.ui.move_history.item(0,0):
            count -= 1
        if not self.ui.move_history.item(rows-1, 1):
            count -= 1
        return count

    def rollBack(self):
        current = self.game.move_number
        try:
            self.game.rollback()
        except InputError as e:
            self.displayMessage(e.msg)
        else:
            row, col = self.moveAt(current)
            it = self.ui.move_history.item(row, col)
            it.setForeground(QBrush(QColor(127,127,127)))
            self.updateBoard()

    def rollForward(self):
        try:
            self.game.rollforward()
        except InputError as e:
            self.displayMessage(e.msg)
        else:
            current = self.game.move_number
            row, col = self.moveAt(current)
            it = self.ui.move_history.item(row, col)
            it.setForeground(QBrush(QColor(0,0,0)))
            self.updateBoard()

    def goToMove(self, move_num: int, color: typing.Literal['black', 'white']):
        move_number = move_num * 2
        if not self.ui.move_history.item(0,0):
            move_number -= 1
        if color == 'white':
            move_number -= 1
        try:
            self.game.go_to_move(move_number)
        except InputError as e:
            self.displayMessage(e.msg)
        else:
            self.ui.move_history.clear()
            self.ui.move_history.setRowCount(1 if color == 'white' else 0)
            for mv in self.game.move_history:
                self.addMoveHistory(str(mv), mv.color)
            i = 0
            while i < len(self.game.future_moves):
                row, col = self.moveAt(self.game.move_number + i + 1)
                mv = self.game.future_moves[::-1][i]
                it = QTableWidgetItem(str(mv))
                it.setForeground(QBrush(QColor(127,127,127)))
                it.setTextAlignment(Qt.AlignCenter)
                if mv.color == 'white':
                    self.ui.move_history.insertRow(row)
                self.ui.move_history.setItem(row, col, it)
                i += 1
            self.updateBoard()

    def displayMessage(self, msg: str):
        dialog = MessageDialog(msg)
        dialog.setParent(self, Qt.Dialog)
        dialog.exec_()

    def widgetAt(self, square: str) -> QFrame | None:
        files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
        file, rank = files.index(square[0]), int(square[1]) - 1
        x = 31 + file * 60
        y = 31 + (7 - rank) * 60
        for frame in self.ui.board.children():
            if isinstance(frame, QFrame) and frame.x() == x and frame.y() == y:
                return frame
        return None

    def square(self, frame: QFrame) -> str:
        file = (frame.x() - 31) // 60
        rank = 8 - ((frame.y() - 31) // 60)
        files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
        return files[file] + str(rank)

    def updateBoard(self):
        self.clear()
        if len(self.game.board.position) > 0:
            for square, piece in self.game.board.position.items():
                square_w = self.widgetAt(square)
                if square_w is None: continue
                label = PieceLabel(piece.type, piece.color)
                label.move(square_w.x(), square_w.y())
                square_w.layout().addWidget(label)
                label.show()

    def clear(self):
        for square in self.ui.board.children():
            if len(square.children()) != 0:
                for child in square.children():
                    if isinstance(child, PieceLabel):
                        child.deleteLater()

class NewGameWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_new_game_dialog()
        self.ui.setupUi(self)
        self.ui.response.accepted.connect(self.startGame)

    def startGame(self):
        main: MainWindow = self.parent()
        if self.ui.custom.isChecked():
            main.ui.view_modes.setCurrentWidget(main.ui.piece_dock)
        else:
            main.ui.view_modes.setCurrentWidget(main.ui.control_panel)
        to_move = 'white' if self.ui.white.isChecked() else 'black'
        main.game = game.Game(to_move=to_move, 
                              standard_position=self.ui.standard.isChecked())
        main.game.parent_window = main
        main.updateBoard()
        main.ui.move_history.clear()
        main.ui.move_history.setRowCount(1)
        self.accept()
