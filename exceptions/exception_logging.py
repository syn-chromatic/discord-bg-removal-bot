import traceback
import logging

logger = logging.getLogger("nextcord")


class ExceptionLogger:
    def __init__(self, exception: Exception):
        self.exception = exception
        self.traceback = exception.__traceback__

    def log(self):
        logging_string = (
            f"Exception: {self.exception}\n"
            f"Traceback: {self.format_traceback_exception()}\n"
        )
        logger.log(logging.ERROR, logging_string)

    def format_traceback(self) -> str:
        frmt_tb = "".join(traceback.format_tb(self.traceback))
        return frmt_tb

    def format_traceback_exception(self) -> str:
        frmt_tb = self.format_traceback()
        return frmt_tb
