from __future__ import annotations
import pieces, board, moves, player
import typing


class Game:
    """Stores information for a game of chess."""
    def __init__(self, *, to_move: typing.Literal['black', 'white'] = 'white',
                 move_history: list[moves.BaseMove] | None = None,
                 standard_position: bool = True):
        self.players = {'black': player.Player('black'),
                        'white': player.Player('white')}
        self.to_move = to_move
        self.move_history = move_history if move_history is not None else []
        self.future_moves = [] # rolling back will add moves here
        self.board = (board.Board.standardPosition() 
                      if standard_position else board.Board())
        
