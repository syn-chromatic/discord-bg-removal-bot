class BaseBotException(Exception):
    """This is a base bot exception."""

    def __init__(self, error: str):
        super().__init__(error)
