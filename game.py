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

    def move(self, start: str, dest: str): # return value used by interface
        """Moves a piece from start to dest."""

        moving_piece = self.board.getPieceAt(start)
        if moving_piece.color != self.to_move:
            pass # UI message: 'You can only move your own pieces.'

        move: moves.BaseMove = moves.Move(start, dest)

        # test for castling
        if (moving_piece.type == 'K' and dest[0] in ('c', 'g')
            and start[1] == dest[1] and self.players[self.to_move].can_castle):
            squares = [file + '1' for file in (('b', 'c', 'd') 
                                               if dest[0] == 'c' 
                                               else ('f', 'g'))]
            if all(not self.board.isOccupied(square) for square in squares):
                pass # UI message 'Illegal move.'
            move = moves.Castle('queenside' if dest[0] == 'c' else 'kingside',
                                self.to_move)
            self.move_history.append(move)
            self.players[self.to_move].can_castle = False
            self.board.move(start, dest)
            return

        if not moving_piece.legal_move(dest):
            pass # UI message: "Illegal move."

        # check pawn moves
        if moving_piece.type == '':
            # straight forward if not blocked
            if (start[0] == dest[0] 
                and not self.board.isOccupied(start[0] + str(int(start[1]) + 1))):
                if dest[1] == '8': 
                    move = moves.Promotion(start, dest)
                    # call UI so user can select piece type to promote to
            elif start[0] != dest[0] and self.board.isOccupied(dest):
                # capturing a piece
                if self.board.getPieceAt(dest).color == self.to_move:
                    return "You can't capture your own pieces."
                if dest[1] == '8': 
                    move = moves.Promotion(start, dest)
                    # call UI so user can select piece type to promote to
                else:
                    move = moves.Capture(start, dest)
            move.color = self.to_move
            move.piece_type = moving_piece.type
            self.move_history.append(move)
            self.board.move(start, dest)
            return