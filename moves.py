import typing
import dataclasses

# contains Move class and its subclasses


@dataclasses.dataclass
class Move:
    """Represents a standard move.
    Stores starting square, destination square, 
    and the type and colour of the moving piece
    """

    start: str
    end: str

    piece_type: typing.Literal['', 'N', 'B', 'K', 'R', 'Q'] = dataclasses.field(init=False)
    color: typing.Literal['black', 'white'] = dataclasses.field(init=False)

    # shows whether string representation requires starting square
    show_start: typing.Literal['none', 'rank', 'file'] = dataclasses.field(init=False)

    def __str__(self) -> str:
        """Returns move in chess notation."""
        start = ''
        if self.show_start == 'file':
            start = self.start[0]
        elif self.show_start == 'rank':
            start = self.start[1]

        return f'{self.piece_type}{start}{self.end}'