class BaseBotException(Exception):
    """This is a base bot exception."""

    def __init__(self, error: str):
        super().__init__(error)


class EmbedFormContextUnavailable(BaseBotException):
    """An exception raised when EmbedForm doesn't have a Context."""

    def __init__(self):
        super().__init__("Context was not set in EmbedForm.")


class EmbedFormMessageUnavailable(BaseBotException):
    """An exception raised when EmbedForm doesn't have a Message."""

    def __init__(self):
        super().__init__("Message is not set in EmbedForm.")


class EmbedFormFileUnavailable(BaseBotException):
    """An exception raised when EmbedForm doesn't have a File."""

    def __init__(self):
        super().__init__("File is not set in EmbedForm.")


class ContextAttachmentUnavailable(BaseBotException):
    """
    An exception raised when an error occurs
    if attachment url is not present in Context.
    """

    def __init__(self):
        super().__init__("Could not retrieve Context attachment URL.")


class MessageNotAvailable(BaseBotException):
    """An exception raised when a user message is not available."""

    def __init__(self):
        super().__init__("Could not access user message.")
