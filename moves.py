import typing
import dataclasses
import abc

# contains Move class and its subclasses


@dataclasses.dataclass()
class BaseMove(abc.ABC):
    """Base class for move types"""
    
    color: typing.Literal['black', 'white'] = dataclasses.field(init=False)
    check: bool = dataclasses.field(init=False, default=False)
    checkmate: bool = dataclasses.field(init=False, default=False)


@dataclasses.dataclass
class Move(BaseMove):
    """Represents a standard move.
    Stores starting square, destination square, 
    and the type and colour of the moving piece
    """

    start: str
    end: str

    piece_type: typing.Literal['', 'N', 'B', 'R', 'K', 'Q'] = dataclasses.field(init=False)

    # shows whether string representation requires starting square
    show_start: typing.Literal['none', 'rank', 'file'] = dataclasses.field(init=False, default='none')

    def __str__(self) -> str:
        """Returns move in chess notation."""
        start = ''
        if self.show_start == 'file':
            start = self.start[0]
        elif self.show_start == 'rank':
            start = self.start[1]

        return (f'{self.piece_type}{start}{self.end}'
                + '#' if self.checkmate else '+' if self.check else '')


@dataclasses.dataclass()
class Capture(Move):
    """Represents a capture move.
    In addition to Move information, store the captured piece's type
    """
    captured_type: typing.Literal['', 'N', 'B', 'R', 'K', 'Q'] = dataclasses.field(init=False)

    def __str__(self) -> str:
        original = str(super())
        return ((original[:-2] if self.piece_type != '' else self.start[0]) 
                + f'x{original[-2:]}')


@dataclasses.dataclass()
class Castle(BaseMove):
    """Represents 'castling'.
    Stores player colour and which side they castled on.
    """
    side: typing.Literal['kingside', 'queenside']

    def __str__(self) -> str:
        end = '#' if self.checkmate else '+' if self.check else ''
        if self.side == 'kingside':
            return 'O-O' + end
        else:
            return 'O-O-O' + end


@dataclasses.dataclass()
class Promotion(Move):
    """Represents promoting a pawn if no capture was required."""
    promote_type: typing.Literal['N', 'B', 'R', 'Q'] = dataclasses.field(init=False)

    def __str__(self):
        return str(super()) + self.promote_type


@dataclasses.dataclass()
class PromotionCapture(Capture):
    """Represents promoting a pawn if pawn made a capture."""
    promote_type: typing.Literal['N', 'B', 'R', 'Q'] = dataclasses.field(init=False)

    def __str__(self):
        return str(super()) + self.promote_type

@dataclasses.dataclass()
class EnPassant(Capture):
    """Represents capturing en-passant."""

    captured_square: str = dataclasses.field(init=False)
