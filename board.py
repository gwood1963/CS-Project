from __future__ import annotations
import dataclasses
import typing
import pieces


@dataclasses.dataclass()
class Board:
    """Represents the current board state.
    Stores the locations of all pieces on the board, accessible by square
    """
    position: dict[str, pieces.Piece] = dataclasses.field(default_factory=dict, init=False)

    def addPiece(self, 
                 piece_type: typing.Literal['', 'N', 'B', 'R', 'Q', 'K'], 
                 square: str, color: typing.Literal['black', 'white']):
        """Adds a piece to the board.
        Creates a new piece using piece_type, square and colour
        and adds it to position using square as the key.
        """
        piece_types = {'': pieces.Pawn, 'N': pieces.Knight, 'B': pieces.Bishop,
                       'R': pieces.Rook, 'Q': pieces.Queen, 'K': pieces.King}
        piece = piece_types[piece_type](square, color)
        self.position[square] = piece

    def getPieceAt(self, square: str) -> pieces.Piece | None:
        """Returns the piece at a given square or None if square is unoccupied."""
        return self.position.get(square)

    def removePieceAt(self, square: str):
        """Removes the piece at a given square.
        Does nothing if square is unnoccopied.
        """
        self.position.pop(square, None)

    def isOccupied(self, square: str) -> bool:
        """Tests if a given square is occupied."""
        return square in self.position

    @classmethod
    def standardPosition(cls) -> Board:
        board = cls()
        for file in ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'):
            board.addPiece('', file + '2', 'white')
            board.addPiece('', file + '7', 'black')
        for file in ('a', 'h'):
            board.addPiece('R', file + '1', 'white')
            board.addPiece('R', file + '8', 'black')
        for file in ('b', 'g'):
            board.addPiece('N', file + '1', 'white')
            board.addPiece('N', file + '8', 'black')
        for file in ('c', 'f'):
            board.addPiece('B', file + '1', 'white')
            board.addPiece('B', file + '8', 'black')
        board.addPiece('Q', 'd1', 'white')
        board.addPiece('Q', 'd8', 'black')
        board.addPiece('K', 'e1', 'white')
        board.addPiece('K', 'e8', 'black')
        return board
    