import dataclasses
import typing


@dataclasses.dataclass()
class Player:
    """Stores information about a player."""

    in_check: bool = dataclasses.field(init=False, default=False)
    can_castle: bool = dataclasses.field(init=False, default=True)
    color: typing.Literal['black', 'white']
