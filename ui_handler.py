from __future__ import annotations

import typing

from PySide6.QtCore import QByteArray, QMargins, QMimeData, Qt
from PySide6.QtGui import (QBrush, QColor, QDrag, QDragEnterEvent,
                           QDragMoveEvent, QDropEvent, QMouseEvent, QPixmap)
from PySide6.QtWidgets import (QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel,
                               QMainWindow, QPushButton, QTableWidgetItem)

import game
from game_window import Ui_MainWindow
from go_to_move import Ui_go_to_move
from input_error import InputError
from message_box import Ui_MessageBox
from new_game_window import Ui_new_game_dialog


class GoToMoveDialog(QDialog):
    '''Dialog displayed when user clicks Go to button.'''
    def __init__(self):
        super().__init__()
        self.ui = Ui_go_to_move()
        self.ui.setupUi(self)
        self.ui.buttonBox.accepted.connect(self.goToMove)

    def goToMove(self):
        main: MainWindow = self.parent()
        text = self.ui.move_num.text().strip()
        if not text.isdecimal():
            main.displayMessage('Invalid move number.')
            return
        move_num = int(text)
        color = 'white' if self.ui.white.isChecked() else 'black'
        main.goToMove(move_num, color)
        self.accept()

class PieceLabel(QLabel):
    '''Class for displaying individual pieces on the board.
    Stores pieece type and color.
    '''
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
    '''Dialog used to display messages to user.'''
    def __init__(self, msg: str):
        super().__init__()
        self.ui = Ui_MessageBox()
        self.ui.setupUi(self)
        self.ui.message_label.setText(msg)

class PromotionDialog(QDialog):
    '''Dialog allowing user to select piece type when promoting a pawn.'''
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
    '''Class represtnting the game's main window.'''
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
        board_layout: QGridLayout = self.ui.board.layout()
        for frame in self.ui.board.children():
            if isinstance(frame, QLabel):
                frame.setStyleSheet('background-color: #363636;\n'
                                    + 'color: #ffffff;')
            elif isinstance(frame, QFrame):
                row, col, *_ = board_layout.getItemPosition(board_layout.indexOf(frame))
                color = '#BFBFBF' if (row + col) % 2 != 0 else '#828282'
                frame.setStyleSheet('background-color: ' + color)
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

        # Handle piece drag and drop
        def dragFromDock(event: QMouseEvent):
            '''Dragging from piece dock in custom position.'''
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
            '''Receiving a piece on the board.'''
            pos = event.pos()

            # find destination square
            square: QFrame
            for frame in self.ui.board.children():
                if isinstance(frame, QFrame) and frame.geometry().contains(pos):
                    square = frame
                    break
            else:
                event.ignore()
                return

            # add piece from dock
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
                    # custom position - don't check legal moves
                    self.game.board.move(start, end)
                    self.updateBoard()

                    if event.source() == self.ui.board:
                        event.setDropAction(Qt.MoveAction)
                        event.accept()
                    else:
                        event.acceptProposedAction()
                else:
                    # attempt move
                    try:
                        self.game.move(start, end)
                    except InputError as msg:
                        # illegal move - display error message
                        self.displayMessage(msg.msg)
                        event.ignore()
                    else:
                        #If move was check or checkmate, display message
                        move = self.game.move_history[-1]
                        if move.checkmate:
                            self.displayMessage('Checkmate.')
                        elif move.check:
                            self.displayMessage('Check.')

                        self.updateBoard()

                        # add move to move history table
                        self.addMoveHistory(str(move), move.color,
                                            self.game.move_history.index(move))

                        if event.source() == self.ui.board:
                            event.setDropAction(Qt.MoveAction)
                            event.accept()
                        else:
                            event.acceptProposedAction()
            else:
                event.ignore()
        self.ui.board.dropEvent = dragToBoard

    def startup(self):
        '''Displays new game dialog.'''
        new = NewGameWindow()
        new.setParent(self, Qt.Dialog)
        new.exec_()

    def openGoToDialog(self):
        goto = GoToMoveDialog()
        goto.setParent(self, Qt.Dialog)
        goto.exec_()

    def setupComplete(self):
        '''Changes view from setup to play.'''
        self.ui.view_modes.setCurrentWidget(self.ui.control_panel)

    def getPromoteType(self) -> typing.Literal['N', 'B', 'R', 'Q']:
        '''Returns type of promoted piece - called by Game.'''
        promote_dialog = PromotionDialog()
        promote_dialog.setParent(self, Qt.Dialog)
        promote_dialog.exec_()
        return self.promote_type

    def addMoveHistory(self, move: str, 
                       color: typing.Literal['black', 'white'], index: int):
        '''Adds move to move history table.'''
        move_entry = QTableWidgetItem(move)
        move_num = self.game.move_number
        rows = self.ui.move_history.rowCount()
        # If move causes future moves to be cleared, remove them from table
        it = self.ui.move_history.item(*self.moveAt(move_num))
        if it:
            self.ui.move_history.clear()
            self.ui.move_history.setRowCount(0)
            for mv in self.game.move_history:
                self.addMoveHistory(str(mv), mv.color, 
                                    self.game.move_history.index(mv))
            return
        # if moving player is white, add new row
        if color == 'white' or index == 0:
            self.ui.move_history.insertRow(rows)
            rows += 1
        col = 0 if color == 'white' else 1
        move_entry.setTextAlignment(Qt.AlignCenter)
        self.ui.move_history.setItem(rows-1, col, move_entry)

    def moveAt(self, current: int) -> tuple[int, int]:
        '''Return indices of current move in table.'''
        if self.ui.move_history.item(0,0):
            return divmod(current-1, 2)
        else:
            return divmod(current, 2)

    def moveCount(self) -> int:
        '''Return number of moves in table.'''
        rows = self.ui.move_history.rowCount()
        count = rows * 2
        if not self.ui.move_history.item(0,0):
            count -= 1
        if not self.ui.move_history.item(rows-1, 1):
            count -= 1
        return count

    def rollBack(self):
        '''Roll back one move.'''
        current = self.game.move_number
        try:
            self.game.rollback()
        except InputError as e:
            self.displayMessage(e.msg)
        else:
            # grey out move in table
            row, col = self.moveAt(current)
            it = self.ui.move_history.item(row, col)
            it.setForeground(QBrush(QColor(127,127,127)))
            self.updateBoard()

    def rollForward(self):
        '''Roll forward one move.'''
        try:
            self.game.rollforward()
        except InputError as e:
            self.displayMessage(e.msg)
        else:
            # change move text color back to black
            current = self.game.move_number
            row, col = self.moveAt(current)
            it = self.ui.move_history.item(row, col)
            it.setForeground(QBrush(QColor(0,0,0)))
            self.updateBoard()

    def goToMove(self, move_num: int, color: typing.Literal['black', 'white']):
        '''Go to a specific move number and color.'''
        move_number = move_num * 2
        white_start = self.ui.move_history.item(0,0)
        if not white_start:
            move_number -= 1
        if color == 'white':
            move_number -= 1
        try:
            self.game.goToMove(move_number)
        except InputError as e:
            self.displayMessage(e.msg)
        else:
            # update table
            self.ui.move_history.clear()
            self.ui.move_history.setRowCount(0)
            for mv in self.game.move_history:
                self.addMoveHistory(str(mv), mv.color,
                                    self.game.move_history.index(mv))
            # future moves greyed out
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
        '''Display message to user.'''
        dialog = MessageDialog(msg)
        dialog.setParent(self, Qt.Dialog)
        dialog.exec_()

    def widgetAt(self, square: str) -> QFrame | None:
        '''Return widget at a specific square.'''
        files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
        file, rank = files.index(square[0]), int(square[1]) - 1
        x = 31 + file * 60
        y = 31 + (7 - rank) * 60
        for frame in self.ui.board.children():
            if isinstance(frame, QFrame) and frame.x() == x and frame.y() == y:
                return frame
        return None

    def square(self, frame: QFrame) -> str:
        '''Return square represented by a given widget.'''
        file = (frame.x() - 31) // 60
        rank = 8 - ((frame.y() - 31) // 60)
        files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
        return files[file] + str(rank)

    def updateBoard(self):
        '''Updates graphical board to reflect board state.'''
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
        '''Clears graphical board.'''
        for square in self.ui.board.children():
            if len(square.children()) != 0:
                for child in square.children():
                    if isinstance(child, PieceLabel):
                        child.deleteLater()

class NewGameWindow(QDialog):
    '''Dialog displayed when starting a new game.'''
    def __init__(self):
        super().__init__()
        self.ui = Ui_new_game_dialog()
        self.ui.setupUi(self)
        self.ui.response.accepted.connect(self.startGame)

    def startGame(self):
        '''Initialises game.'''
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
        main.ui.move_history.setRowCount(0)
        self.accept()
