from exceptions.bot_exceptions import BaseBotException


class ResponseConnectionError(BaseBotException):
    """An exception raised when a connection error occurs during HTTP connection."""

    def __init__(self):
        super().__init__("Connection error occurred.")


class ResponseContentError(BaseBotException):
    """An exception raised when an error occurs while reading an HTTP response."""

    def __init__(self):
        super().__init__("Could not retrieve Response Content.")


class UnsupportedMimeType(BaseBotException):
    """An exception raised when an unsupported mime type is detected."""

    def __init__(self, mime_type: str):
        msg = "Detected file mime type as: " f"'{mime_type}', which is not supported."
        super().__init__(msg)
