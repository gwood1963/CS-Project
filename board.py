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

    files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')

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

    def getPieceAt(self, square: str) -> pieces.Piece:
        """Returns the piece at a given square."""
        return self.position[square]

    def removePieceAt(self, square: str):
        """Removes the piece at a given square.
        Does nothing if square is unnoccopied.
        """
        self.position.pop(square, None)

    def isOccupied(self, square: str) -> bool:
        """Tests if a given square is occupied."""
        return square in self.position

    def getPieces(self, *, color: typing.Literal['black', 'white'] | None = None,
                  type: typing.Literal['', 'N', 'B', 'R', 'Q', 'K'] | None = None):
        """Returns all pieces that satisfy a condition
        e.g. all white pieces, all rooks, all black knights
        """
        filters = []
        if color is not None:
            def f1(p: pieces.Piece): return p.color == color
            filters.append(f1)
        if type is not None:
            def f2(p: pieces.Piece): return p.type == type
            filters.append(f2)
        return [piece for piece in self.position.values() 
                if all(f(piece) for f in filters)]

    def scanDiagonals(self, square: str) -> list[pieces.Piece]:
        """Returns first piece on each diagonal from square."""
        rank, file = int(square[1]), self.files.index(square[0])
        directions = ((1,1), (-1,1), (-1,-1), (1,-1))
        pieces = []
        for direction in directions:
            r, f = rank + direction[1], file + direction[0]
            while 1 <= r <= 8 and 0 <= f <= 7:
                s = self.files[f] + str(r)
                if self.isOccupied(s):
                    pieces.append(self.getPieceAt(s))
                    break
                r += direction[1]
                f += direction[0]
        return pieces

    def scanRankandFile(self, square: str) -> list[pieces.Piece]:
        """Returns first pieces on rank and file in each direction from square."""
        rank, file = int(square[1]), self.files.index(square[0])
        directions = ((1,0), (0,1), (-1,0), (0,-1))
        pieces = []
        for direction in directions:
            r, f = rank + direction[1], file + direction[0]
            while 1 <= r <= 8 and 0 <= f <= 7:
                s = self.files[f] + str(r)
                if self.isOccupied(s):
                    pieces.append(self.getPieceAt(s))
                    break
                r += direction[1]
                f += direction[0]
        return pieces

    def move(self, start: str, end: str):
        """Moves a piece on the board."""
        if self.isOccupied(start) and not self.isOccupied(end):
            self.position[end] = self.position[start]
            self.removePieceAt(start)

    @classmethod
    def standardPosition(cls) -> Board:
        board = cls()
        for file in cls.files:
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
    