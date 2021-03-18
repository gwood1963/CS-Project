import typing
import dataclasses
import abc


@dataclasses.dataclass()
class Piece(abc.ABC):
    """Represents a single piece."""

    square: str
    color: typing.Literal['black', 'white']

    @property
    @abc.abstractmethod
    def type(self) -> typing.Literal['', 'N', 'B', 'R', 'Q', 'K']:
        """Returns piece type."""

    @abc.abstractmethod
    def legal_move(self, dest: str) -> bool:
        """Tests if the piece can move to a given square."""

    def move(self, dest: str):
        self.square = dest


@dataclasses.dataclass()
class Pawn(Piece):
    @property
    def type(self):
        return ''
    
    def legal_move(self, dest: str) -> bool:
        files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
        if abs(files.index(self.square[0]) - files.index(dest[0])) > 1:
            return False
        elif self.color == 'black':
            if int(self.square[1]) - int(dest[1]) == 2:
                return self.square[1] == '7'
            elif int(self.square[1]) - int(dest[1]) == 1:
                return True
            else:
                return False
        else: # colour is white
            if int(dest[1]) - int(self.square[1]) == 2:
                return self.square[1] == '2'
            elif int(dest[1]) - int(self.square[1]) == 1:
                return True
            else:
                return False


@dataclasses.dataclass()
class Knight(Piece):
    @property
    def type(self):
        return 'N'

    def legal_move(self, dest: str) -> bool:
        files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
        rank_diff = abs(int(dest[1]) - int(self.square[1]))
        file_diff = abs(files.index(dest[0]) - files.index(self.square[0]))
        return (rank_diff, file_diff) in ((1,2), (2,1))


@dataclasses.dataclass()
class Bishop(Piece):
    @property
    def type(self):
        return 'B'
        
    def legal_move(self, dest: str) -> bool:
        files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
        rank_diff = abs(int(dest[1]) - int(self.square[1]))
        file_diff = abs(files.index(dest[0]) - files.index(self.square[0]))
        return rank_diff == file_diff


@dataclasses.dataclass()
class Rook(Piece):
    @property
    def type(self):
        return 'R'

    def legal_move(self, dest: str) -> bool:
        files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
        rank_diff = abs(int(dest[1]) - int(self.square[1]))
        file_diff = abs(files.index(dest[0]) - files.index(self.square[0]))
        return 0 in (rank_diff, file_diff)


@dataclasses.dataclass()
class Queen(Piece):
    @property
    def type(self):
        return 'Q'

    def legal_move(self, dest: str) -> bool:
        files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
        rank_diff = abs(int(dest[1]) - int(self.square[1]))
        file_diff = abs(files.index(dest[0]) - files.index(self.square[0]))
        return 0 in (rank_diff, file_diff) or rank_diff == file_diff


@dataclasses.dataclass()
class King(Piece):
    @property
    def type(self):
        return 'K'

    def legal_move(self, dest: str) -> bool:
        files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
        rank_diff = abs(int(dest[1]) - int(self.square[1]))
        file_diff = abs(files.index(dest[0]) - files.index(self.square[0]))
        return rank_diff in (0,1) and file_diff in (0,1)
