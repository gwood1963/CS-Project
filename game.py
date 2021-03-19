from __future__ import annotations
import board, moves, player
import typing
import input_error
import ui_handler

class Game:
    """Stores information for a game of chess."""

    files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')

    def __init__(self, *, to_move: typing.Literal['black', 'white'] = 'white',
                 move_history: list[moves.BaseMove] | None = None,
                 standard_position: bool = True):
        self.players = {'black': player.Player('black'),
                        'white': player.Player('white')}
        self.to_move: typing.Literal['black', 'white'] = to_move
        self.move_history: list[moves.BaseMove] = (
            move_history if move_history is not None else []
        )
        self.future_moves: list[moves.BaseMove] = [] # rolling back will add moves here
        self.board = (board.Board.standardPosition() 
                      if standard_position else board.Board())
        self.game_over = False
        self.move_number: int = 0
        self.parent_window: ui_handler.MainWindow

    def threatened(self, square: str, opponent: typing.Literal['black', 'white']) -> bool:
        """Checks if square is threatened by opponent."""
        pawns = self.board.getPieces(color=opponent, type=[''])
        f1, f2 = self.files.index(square[0]) + 1, self.files.index(square[0]) - 1
        if any(p.square[0] in (f1,f2) and p.legalMove(square) for p in pawns):
            return True
        elif any(piece.color == opponent and piece.legalMove(square) 
                 for piece in self.board.scanDiagonals(square)):
            return True
        elif any(piece.color == opponent and piece.type != '' and piece.legalMove(square) 
                 for piece in self.board.scanRankandFile(square)):
            return True
        elif any(piece.legalMove(square) 
                 for piece in self.board.getPieces(type=['N'], color=opponent)):
            return True
        else:
            return False

    def inCheck(self, color: typing.Literal['black', 'white']) -> bool:
        """Checks if the given player is in check."""
        kings = self.board.getPieces(color=color, type=['K'])
        if len(kings) == 0:
            return False
        king = kings[0]
        opponent = 'black' if color == 'white' else 'white'
        return self.threatened(king.square, opponent)

    def checkmated(self, color: typing.Literal['black', 'white'], check: moves.Move) -> bool:
        kings = self.board.getPieces(color=color, type=['K'])
        if len(kings) == 0:
            return False
        king = kings[0]

        # can king move?
        adjacent = self.board.adjacentSquares(king.square)
        for square in adjacent:
            if ((not self.board.isOccupied(square)
                 or self.board.getPieceAt(square).color != color)
                and not self.threatened(square, check.color)):
                try:
                    self.move(king.square, square)
                except input_error.InputError:
                    return True
                return False
            
        check_square = check.end
        
        # can checking piece be captured?
        if self.threatened(check_square, color):
            for piece in (self.board.getPieces(color=color, type=['N', 'K', ''])
                          + self.board.scanDiagonals(check_square) 
                          + self.board.scanRankandFile(check_square)):
                if (piece.color == color and piece.legalMove(check_square)
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
                    if (piece.color == color and piece.legalMove(check_square)
                        and piece.type != ''):
                        self.board.move(piece.square, check_square)
                        still_in_check = self.inCheck(color)
                        self.board.move(check_square, piece.square)
                        if not still_in_check:
                            return False
            for pawn in self.board.getPieces(color=color, type=['']):
                if pawn.square[0] == square[0] and pawn.legalMove(square):
                    return False
        return True

    def rollback(self, mv: moves.BaseMove | None = None):
        """Rolls back one move.
        Will roll back last move by default,
        mv parameter should only be used to undo a move 
        that has not been added to move_history yet
        (move does this to test if a move will leave the king in check)
        """
        if len(self.move_history) == 0:
            raise input_error.InputError('No moves to roll back.')
        move = self.move_history.pop() if mv is None else mv
        
        opponent = 'black' if move.color == 'white' else 'white'
        
        if isinstance(move, moves.Castle):
            rank = '1' if move.color == 'white' else '8'
            
            if move.side == 'queenside':
                self.board.move('c' + rank, 'e' + rank)
                self.board.move('d' + rank, 'a' + rank)
            else: # side == 'kingside'
                self.board.move('g' + rank, 'e' + rank)
                self.board.move('f' + rank, 'h' + rank)
            self.players[move.color].can_castle = True
            
        elif isinstance(move, moves.Move):
            # return moving piece to starting square
            if (isinstance(move, moves.Promotion) 
                or isinstance(move, moves.PromotionCapture)):
                # if move is a promotion a new pawn needs to be created
                self.board.addPiece('', move.start, move.color)
                self.board.removePieceAt(move.end)
            else:
                self.board.move(move.end, move.start)

            # replace captured piece
            if isinstance(move, moves.EnPassant):
                self.board.addPiece(move.captured_type, 
                                    move.captured_square, opponent)
            elif isinstance(move, moves.Capture):
                self.board.addPiece(move.captured_type, move.end, opponent)

        # update game info
        if move.check:
            self.players[opponent].in_check = False
        self.game_over = False
        self.future_moves.append(move)
        self.move_number -= 1
        self.to_move = move.color

    def rollforward(self, mv: moves.BaseMove | None = None):
        """Rolls forward one move.
        parameter allows move to be specified - will be used for multiplayer
        uses first move from move_history if mv not specified
        """
        if mv is not None:
            self.future_moves.clear()
            move = mv
        elif len(self.future_moves) == 0:
            raise input_error.InputError('No moves to roll forward.')
        else:
            move = self.future_moves.pop()
        
        opponent = 'black' if move.color == 'white' else 'white'
        
        if isinstance(move, moves.Castle):
            rank = '1' if move.color == 'white' else '8'
            
            if move.side == 'queenside':
                self.board.move('e' + rank, 'c' + rank)
                self.board.move('a' + rank, 'd' + rank)
            else: # side == 'kingside'
                self.board.move('e' + rank, 'g' + rank)
                self.board.move('h' + rank, 'f' + rank)
            self.players[move.color].can_castle = False
            
        elif isinstance(move, moves.Move):
            # remove captured piece
            if isinstance(move, moves.EnPassant):
                self.board.removePieceAt(move.captured_square)
            elif isinstance(move, moves.Capture):
                self.board.removePieceAt(move.end)
            
            # move piece
            if (isinstance(move, moves.Promotion) 
                or isinstance(move, moves.PromotionCapture)):
                # if move is a promotion a new pawn needs to be created
                self.board.addPiece(move.promote_type, move.end, move.color)
                self.board.removePieceAt(move.start)
            else:
                self.board.move(move.start, move.end)

        # update game info
        if move.check:
            self.players[opponent].in_check = True
        if move.checkmate:
            self.game_over = False
        self.move_history.append(move)
        self.move_number += 1
        self.to_move = opponent

    def goToMove(self, move_number: int):
        if not 0 <= move_number <= self.move_number + len(self.future_moves):
            raise input_error.InputError('Invalid move number.')
        elif move_number < self.move_number:
            while self.move_number != move_number:
                self.rollback()
        elif move_number > self.move_number:
            while self.move_number != move_number:
                self.rollforward()

    def move(self, start: str, dest: str):
        """Moves a piece from start to dest."""

        # if no move is made, do nothing
        if start == dest:
            return

        # do nothing if game is over
        if self.game_over:
            raise input_error.InputError('The game is over.')

        current = self.to_move
        opponent = 'black' if current == 'white' else 'white'
        moving_piece = self.board.getPieceAt(start)
        if moving_piece.color != current:
            raise input_error.InputError('You can only move your own pieces.')

        move: moves.BaseMove = moves.Move(start, dest)

        # test for castling
        if (moving_piece.type == 'K' and dest[0] in ('c', 'g')
            and start[1] == dest[1]):
            if not self.players[current].can_castle or self.players[current].in_check:
                raise input_error.InputError('Illegal move.')
            # check rook is present
            rook_square = ('a' if dest[0] == 'c' else 'h') + dest[1]
            if (not self.board.isOccupied(rook_square) 
                or self.board.getPieceAt(rook_square).type != 'R'):
                raise input_error.InputError('Illegal move.')
            # check intervening squares
            squares = [file + dest[1] for file in (('b', 'c', 'd') 
                                                   if dest[0] == 'c' 
                                                   else ('f', 'g'))]
            if any(self.board.isOccupied(square) for square in squares):
                raise input_error.InputError('Illegal move.')
            intermediate = ('d' if dest[0] == 'c' else 'f') + dest[1]
            if self.threatened(dest, opponent) or self.threatened(intermediate, opponent):
                raise input_error.InputError('You cannot castle into or across check.')
            move = moves.Castle('queenside' if dest[0] == 'c' else 'kingside')
            move.color = current
            self.players[current].can_castle = False
            self.board.move(start, dest)
            # move the rook
            if dest[0] == 'c':
                self.board.move('a'+start[1], 'd'+start[1])
            elif dest[0] == 'g':
                self.board.move('h'+start[1], 'f'+start[1])
            if self.inCheck(current):
                self.rollback(move)
                raise input_error.InputError('You cannot move into check.')
            if self.inCheck(opponent):
                self.players[opponent].in_check = True
                move.check = True
            self.to_move = opponent
            self.move_history.append(move)
            self.move_number += 1
            return

        if not moving_piece.legalMove(dest):
            raise input_error.InputError('Illegal move.')

        # check pawn moves
        elif moving_piece.type == '':
            # straight forward if not blocked
            if (start[0] == dest[0] and not self.board.isOccupied(dest)):
                if self.board.isOccupied(
                    start[0] + str(int(start[1]) 
                                   + (1 if current == 'white' else -1))
                ):
                    raise input_error.InputError('Illegal move.')
                if dest[1] == ('8' if current == 'white' else '1'): 
                    move = moves.Promotion(start, dest)
                    move.promote_type = self.parent_window.getPromoteType()
            elif start[0] != dest[0] and self.board.isOccupied(dest):
                # capturing a piece
                if self.board.getPieceAt(dest).color == current:
                    raise input_error.InputError('You cannot capture your own pieces.')
                if dest[1] == ('8' if current == 'white' else '1'): 
                    move = moves.PromotionCapture(start, dest)
                    move.promote_type = self.parent_window.getPromoteType()
                else:
                    move = moves.Capture(start, dest)
            elif start[0] != dest[0] and not self.board.isOccupied(dest):
                # check en-passant capture
                square = dest[0] + start[1]
                last_move = self.move_history[-1]
                if (isinstance(last_move, moves.Move) and last_move.end == square
                    and last_move.piece_type == ''
                    and last_move.start == dest[0] + ('7' if opponent == 'black' else '2')):
                    move = moves.EnPassant(start, dest)
                    move.captured_square = square
                else:
                    raise input_error.InputError('Illegal move.')

        # check knight move
        elif moving_piece.type == 'N':
            if self.board.isOccupied(dest):
                if self.board.getPieceAt(dest).color == current:
                    raise input_error.InputError("You can't capture your own pieces.")
                move = moves.Capture(start, dest)

        # check bishop, rook or queen move
        elif moving_piece.type in ('B', 'R', 'Q'):
            # check intervening squares
            squares = self.board.interveningSquares(start, dest)
            if any(self.board.isOccupied(square) for square in squares):
                print(squares)
                raise input_error.InputError('You cannot jump over other pieces.')
            if self.board.isOccupied(dest):
                if self.board.getPieceAt(dest).color == current:
                    raise input_error.InputError("You can't capture your own pieces.")
                move = moves.Capture(start, dest)

        # check king move
        elif moving_piece.type == 'K':
            if self.threatened(dest, opponent):
                raise input_error.InputError('You cannot move into check.')
            if self.board.isOccupied(dest):
                if self.board.getPieceAt(dest).color == current:
                    raise input_error.InputError("You can't capture your own pieces.")
                move = moves.Capture(start, dest)

        if isinstance(move, moves.Capture):
            captured_square = dest
            if isinstance(move, moves.EnPassant):
                captured_square = move.captured_square
            move.captured_type = self.board.getPieceAt(captured_square).type
            self.board.removePieceAt(captured_square)
        move.color = current
        move.piece_type = moving_piece.type
        if isinstance(move, moves.Promotion) or isinstance(move, moves.PromotionCapture):
            self.board.addPiece(move.promote_type, move.end, current)
            self.board.removePieceAt(move.start)
        else:
            self.board.move(start, dest)
            moving_piece.square = dest
        
        # check if new position puts a player in check
        if self.inCheck(current):
            self.rollback(move)
            raise input_error.InputError('You cannot make a move that would leave your king in check.')
        elif self.players[current].in_check:
            self.players[current].in_check = False
        if self.inCheck(opponent):
            self.players[opponent].in_check = True
            move.check = True
            if self.checkmated(opponent, move):
                move.checkmate = True
                self.game_over = True

        if moving_piece.type == 'K':
            self.players[current].can_castle = False
        self.move_history.append(move)
        self.future_moves.clear()
        self.move_number += 1
        self.to_move = opponent
