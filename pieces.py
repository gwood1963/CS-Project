import typing
import dataclasses
import abc


@dataclasses.dataclass()
class Piece(abc.ABC):
    """Represents a single piece."""

    square: str
    color: typing.Literal['black', 'white']

    @abc.abstractmethod
    def legal_move(square: str) -> bool:
        """Tests if the piece can move to a given square."""