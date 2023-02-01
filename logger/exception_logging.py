import traceback
import logging

logger = logging.getLogger("nextcord")


class ExceptionLogger:
    def __init__(self, exception: Exception):
        self.exception = exception
        self.traceback = exception.__traceback__

    def log(self, message: str = ""):
        logging_string = (f"Exception: {self.exception}\n")
        exception_traceback = self.format_traceback_exception()
        if exception_traceback:
            traceback_string = f"Traceback:\n{exception_traceback}\n"
            logging_string += traceback_string
        if message:
            message_str = f"Message: {message}\n"
            logging_string += message_str

        logger.log(logging.ERROR, logging_string)

    def format_traceback(self) -> str:
        frmt_tb = "".join(traceback.format_tb(self.traceback))
        frmt_tb = frmt_tb.strip()
        return frmt_tb

    def format_traceback_exception(self) -> str:
        frmt_tb = self.format_traceback()
        return frmt_tb
