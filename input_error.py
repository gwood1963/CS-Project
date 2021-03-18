class InputError(Exception):
    """Custom exception thrown by game to communicate with UI.
    Thrown on illegal move or if user tries to go to a nonexistent move number."""

    def __init__(self, msg: str):
        self.msg = msg