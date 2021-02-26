from __future__ import annotations
import board, moves, player
import typing


class Game:
    files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')

    """Stores information for a game of chess."""
    def __init__(self, *, to_move: typing.Literal['black', 'white'] = 'white',
                 move_history: list[moves.BaseMove] | None = None,
                 standard_position: bool = True):
        self.players = {'black': player.Player('black'),
                        'white': player.Player('white')}
        self.to_move: typing.Literal['black', 'white'] = to_move
        self.move_history = move_history if move_history is not None else []
        self.future_moves = [] # rolling back will add moves here
        self.board = (board.Board.standardPosition() 
                      if standard_position else board.Board())

    def inCheck(self, color: typing.Literal['black', 'white']) -> bool:
        king = self.board.getPieces(color=color, type=['K'])[0]
        opponent = 'black' if color == 'white' else 'white'
        pawns = self.board.getPieces(color=opponent, type=[''])
        f1, f2 = self.files.index(king.square[0]) + 1, self.files.index(king.square[0]) - 1
        r = int(king.square[1]) + 1 if color == 'white' else -1
        if any(p.square in (self.files[f1] + str(r), self.files[f2] + str(r)) 
               for p in pawns):
            return True
        elif any(piece.color == opponent and piece.legal_move(king.square) 
                 for piece in self.board.scanDiagonals(king.square)):
            return True
        elif any(piece.color == opponent and piece.legal_move(king.square) 
                 for piece in self.board.scanRankandFile(king.square)):
            return True
        elif any(piece.legal_move(king.square) 
                 for piece in self.board.getPieces(type=['N'], color=opponent)):
            return True
        else:
            return False

    def move(self, start: str, dest: str): # return value used by interface
        """Moves a piece from start to dest."""

        current = self.to_move
        opponent = 'black' if current == 'white' else 'white'
        moving_piece = self.board.getPieceAt(start)
        if moving_piece.color != current:
            # UI message: 'You can only move your own pieces.'
            return

        move: moves.BaseMove = moves.Move(start, dest)

        # test for castling
        if (moving_piece.type == 'K' and dest[0] in ('c', 'g')
            and start[1] == dest[1]):
            if not self.players[current].can_castle or self.players[current].in_check:
                # UI message: Illegal move.
                return
            # check intervening squares
            squares = [file + '1' for file in (('b', 'c', 'd') 
                                               if dest[0] == 'c' 
                                               else ('f', 'g'))]
            if any(self.board.isOccupied(square) for square in squares):
                # UI message 'Illegal move.'
                return
            move = moves.Castle('queenside' if dest[0] == 'c' else 'kingside',
                                current)
            self.move_history.append(move)
            self.players[current].can_castle = False
            self.board.move(start, dest)
            if dest[0] == 'c':
                self.board.move('a'+start[1], 'd'+start[1])
            elif dest[0] == 'g':
                self.board.move('h'+start[1], 'f'+start[1])
            if self.inCheck(current):
                # roll back position
                # UI alert: Illegal move.
                return
            if self.inCheck(opponent):
                self.players[opponent].in_check = True
                move.check = True
                # UI message: check
            return

        if not moving_piece.legal_move(dest):
            # UI message: "Illegal move."
            return

        # check pawn moves
        elif moving_piece.type == '':
            # straight forward if not blocked
            if (start[0] == dest[0] and not self.board.isOccupied(dest)):
                if self.board.isOccupied(
                    start[0] + str(int(start[1]) 
                                   + 1 if current == 'white' else -1)
                ):
                    # UI message: Illegal move.
                    return
                if dest[1] == '8': 
                    move = moves.Promotion(start, dest)
                    # call UI so user can select piece type to promote to
            elif start[0] != dest[0] and self.board.isOccupied(dest):
                # capturing a piece
                if self.board.getPieceAt(dest).color == current:
                    # UI message: "You can't capture your own pieces."
                    return
                if dest[1] == '8': 
                    move = moves.PromotionCapture(start, dest)
                    # call UI so user can select piece type to promote to
                else:
                    move = moves.Capture(start, dest)
            elif start[0] != dest[0] and not self.board.isOccupied(dest):
                # check en-passant capture
                square = dest[0] + start[1]
                last_move = self.move_history[-1]
                if (isinstance(last_move, moves.Move) and last_move.end == square
                    and last_move.piece_type == ''
                    and last_move.start == dest[0] + '7' if opponent == 'black' else '2'):
                    move = moves.EnPassant(start, dest)
                    move.captured_square = square
                else:
                    # UI message: Illegal move.
                    return

        # check knight move
        elif moving_piece.type == 'N':
            if self.board.isOccupied(dest):
                if self.board.getPieceAt(dest).color == current:
                    # UI message: "You can't capture your own pieces."
                    return
                move = moves.Capture(start, dest)

        # check bishop move
        elif moving_piece.type == 'B':
            # check intervening squares
            r1, r2 = min(int(start[1]), int(dest[1])), max(int(start[1]), int(dest[1]))
            f1 = min(self.files.index(start[0]), self.files.index(dest[0]))
            f2 = max(self.files.index(start[0]), self.files.index(dest[0]))
            squares = [self.files[f] + str(r) for f,r in (range(f1+1, f2), range(r1+1, r2))]
            if any(self.board.isOccupied(square) for square in squares):
                # UI message: Illegal move.
                return
            if self.board.isOccupied(dest):
                if self.board.getPieceAt(dest).color == current:
                    # UI message: "You can't capture your own pieces."
                    return
                move = moves.Capture(start, dest)

        # check rook move
        elif moving_piece.type == 'R':
            # check intervening squares
            if start[0] == dest[0]:
                r1, r2 = min(int(start[1]), int(dest[1])), max(int(start[1]), int(dest[1]))
                squares = [start[0] + str(r) for r in range(r1+1, r2)]
            else:
                f1 = min(self.files.index(start[0]), self.files.index(dest[0]))
                f2 = max(self.files.index(start[0]), self.files.index(dest[0]))
                squares = [self.files[f] + start[1] for f in range(f1+1, f2)]
            if any(self.board.isOccupied(square) for square in squares):
                # UI message: Illegal move.
                return
            if self.board.isOccupied(dest):
                if self.board.getPieceAt(dest).color == current:
                    # UI message: "You can't capture your own pieces."
                    return
                move = moves.Capture(start, dest)

        # check queen move
        elif moving_piece.type == 'Q':
            # check intervening squares
            if start[0] == dest[0]:
                r1, r2 = min(int(start[1]), int(dest[1])), max(int(start[1]), int(dest[1]))
                squares = [start[0] + str(r) for r in range(r1+1, r2)]
            elif start[1] == dest[1]:
                f1 = min(self.files.index(start[0]), self.files.index(dest[0]))
                f2 = max(self.files.index(start[0]), self.files.index(dest[0]))
                squares = [self.files[f] + start[1] for f in range(f1+1, f2)]
            else:
                r1, r2 = min(int(start[1]), int(dest[1])), max(int(start[1]), int(dest[1]))
                f1 = min(self.files.index(start[0]), self.files.index(dest[0]))
                f2 = max(self.files.index(start[0]), self.files.index(dest[0]))
                squares = [self.files[f] + str(r) for f,r in (range(f1+1, f2), range(r1+1, r2))]
            if any(self.board.isOccupied(square) for square in squares):
                # UI message: Illegal move.
                return
            if self.board.isOccupied(dest):
                if self.board.getPieceAt(dest).color == current:
                    # UI message: "You can't capture your own pieces."
                    return
                move = moves.Capture(start, dest)

        # check king move
        elif moving_piece.type == 'K':
            if self.board.isOccupied(dest):
                if self.board.getPieceAt(dest).color == current:
                    # UI message: "You can't capture your own pieces."
                    return
                move = moves.Capture(start, dest)

        if isinstance(move, moves.Capture):
            captured_square = dest
            if isinstance(move, moves.EnPassant):
                captured_square = move.captured_square
            move.captured_type = self.board.getPieceAt(captured_square).type
            self.board.removePieceAt(captured_square)
        move.color = current
        move.piece_type = moving_piece.type
        self.board.move(start, dest)
        moving_piece.square = dest
        
        # check if new position puts a player in check
        if self.inCheck(current):
            # roll back position
            # UI alert: Illegal move.
            return
        elif self.players[current].in_check:
            self.players[current].in_check = False
        if self.inCheck(opponent):
            self.players[opponent].in_check = True
            move.check = True
            # UI message: check
        
        self.move_history.append(move)
        self.to_move = opponent
        # update UI
