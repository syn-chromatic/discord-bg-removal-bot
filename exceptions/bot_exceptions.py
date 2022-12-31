class BaseBotException(Exception):
    """This is a base bot exception."""

    def __init__(self, error: str):
        super().__init__(error)


class ContextAttachmentUnavailable(BaseBotException):
    """
    An exception raised when an error occurs
    if attachment url is not present in Context.
    """

    def __init__(self):
        super().__init__("Could not retrieve attachment URL.")
