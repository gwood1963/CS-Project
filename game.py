from __future__ import annotations
import board, moves, player
import typing


class Game:
    """Stores information for a game of chess."""

    files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')

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
        self.game_over = False

    def threatened(self, square: str, opponent: typing.Literal['black', 'white']) -> bool:
        """Checks if square is threatened by opponent."""
        pawns = self.board.getPieces(color=opponent, type=[''])
        f1, f2 = self.files.index(square[0]) + 1, self.files.index(square[0]) - 1
        if any(p.square[0] in (f1,f2) and p.legal_move(square) for p in pawns):
            return True
        elif any(piece.color == opponent and piece.legal_move(square) 
                 for piece in self.board.scanDiagonals(square)):
            return True
        elif any(piece.color == opponent and piece.legal_move(square) 
                 for piece in self.board.scanRankandFile(square)):
            return True
        elif any(piece.legal_move(square) 
                 for piece in self.board.getPieces(type=['N'], color=opponent)):
            return True
        else:
            return False

    def inCheck(self, color: typing.Literal['black', 'white']) -> bool:
        """Checks if the given player is in check."""
        king = self.board.getPieces(color=color, type=['K'])[0]
        opponent = 'black' if color == 'white' else 'white'
        return self.threatened(king.square, opponent)

    def checkmated(self, color: typing.Literal['black', 'white'], check: moves.Move) -> bool:
        king = self.board.getPieces(color=color, type=['K'])[0]
        adjacent = self.board.adjacentSquares(king.square)
        for square in adjacent:
            if ((not self.board.isOccupied(square)
                 or self.board.getPieceAt(square).color != color)
                and not self.threatened(square, check.color)):
                return False
        check_square = check.end
        # can checking piece be captured?
        if self.threatened(check_square, color):
            for piece in (self.board.getPieces(color=color, type=['N', 'K', ''])
                          + self.board.scanDiagonals(check_square) 
                          + self.board.scanRankandFile(check_square)):
                if (piece.color == color and piece.legal_move(check_square)
                    and (piece.type != '' 
                         or piece.square[0] != check_square[0])):
                    self.board.removePieceAt(check_square)
                    self.board.move(piece.square, check_square)
                    still_in_check = self.inCheck(color)
                    self.board.move(check_square, piece.square)
                    self.board.addPiece(check.piece_type, check_square, check.color)
                    if not still_in_check:
                        return False
        # can check be blocked?
        intervening = self.board.interveningSquares(king.square, check_square)
        for square in intervening:
            if self.threatened(square, color):
                for piece in (self.board.getPieces(color=color, type=['N', 'K'])
                              + self.board.scanDiagonals(check_square) 
                              + self.board.scanRankandFile(check_square)):
                    if (piece.color == color and piece.legal_move(check_square)
                        and piece.type != ''):
                        self.board.move(piece.square, check_square)
                        still_in_check = self.inCheck(color)
                        self.board.move(check_square, piece.square)
                        if not still_in_check:
                            return False
            for pawn in self.board.getPieces(color=color, type=['']):
                if pawn.square[0] == square[0] and pawn.legal_move(square):
                    return False
        return True

    def move(self, start: str, dest: str): # return value used by interface
        """Moves a piece from start to dest."""

        # do nothing if game is over
        if self.game_over:
            return

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
            # check rook is present
            rook_square = ('a' if dest[0] == 'c' else 'h') + dest[1]
            if (not self.board.isOccupied(rook_square) 
                or self.board.getPieceAt(rook_square).type != 'R'):
                # UI message: Illegal move.
                return
            # check intervening squares
            squares = [file + '1' for file in (('b', 'c', 'd') 
                                               if dest[0] == 'c' 
                                               else ('f', 'g'))]
            if any(self.board.isOccupied(square) for square in squares):
                # UI message 'Illegal move.'
                return
            intermediate = ('d' if dest[0] == 'c' else 'f') + dest[1]
            if self.threatened(dest, opponent) or self.threatened(intermediate, opponent):
                # UI message: Illegal move.
                return
            move = moves.Castle('queenside' if dest[0] == 'c' else 'kingside',
                                current)
            self.players[current].can_castle = False
            self.board.move(start, dest)
            # move the rook
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
            self.move_history.append(move)
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

        # check bishop, rook or queen move
        elif moving_piece.type in ('B', 'R', 'Q'):
            # check intervening squares
            squares = self.board.interveningSquares(start, dest)
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
            if self.threatened(dest, opponent):
                # UI message: Illegal move.
                return
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
            if self.checkmated(opponent, move):
                # UI message: checkmate
                move.checkmate = True
                self.game_over = True
            else:
                # UI message: check
                pass
        
        self.move_history.append(move)
        self.to_move = opponent
        # update UI
