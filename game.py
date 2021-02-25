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

    def move(self, start: str, dest: str) -> str | None: # return value used by interface
        """Moves a piece from start to dest."""

        moving_piece = self.board.getPieceAt(start)
        if moving_piece is None:
            return None # nothing hammens if there's no piece to move
        elif moving_piece.color != self.to_move:
            return 'You can only move your own pieces.'

        move: moves.BaseMove

        # test for castling
        if (moving_piece.type == 'K' and dest[0] in ('c', 'g')
            and start[1] == dest[1] and self.players[self.to_move].can_castle):
            squares = [file + '1' for file in (('b', 'c', 'd') 
                                               if dest[0] == 'c' 
                                               else ('f', 'g'))]
            if all(not self.board.isOccupied(square) for square in squares):
                return 'Illegal move.'
            move = moves.Castle('queenside' if dest[0] == 'c' else 'kingside',
                                self.to_move)
            self.move_history.append(move)
            self.players[self.to_move].can_castle = False
            return 'success'
            
