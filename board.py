from __future__ import annotations
import dataclasses
import pieces


@dataclasses.dataclass()
class Board:
    """Represents the current board state.
    Stores the locations of all pieces on the board, accessible by square
    """
    position: dict[str, pieces.Piece] = dataclasses.field(default_factory=dict, init=False)
    