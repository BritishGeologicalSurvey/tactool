"""
Module for utilities and functions to help with development.
"""
import logging

from PyQt5.QtCore import pyqtRemoveInputHook

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(asctime)s %(name)s: %(message)s",
    datefmt="{%Y-%m-%d %H:%M:%S}",
)


class LoggerMixin:
    """
    Logger class to give each class of the TACtool application a built-in logger.
    """
    def __init__(self):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)


    @staticmethod
    def _set_logger_levels(level: int) -> None:
        """
        Set the logger levels across all classes in the TACtool application.
        """
        top_level = LoggerMixin
        children = [top_level] + top_level.__subclasses__()
        for child in children:
            logger = logging.getLogger(child.__name__)
            logger.setLevel(level)


def ipdb_breakpoint():
    """
    Drops code into IPYthon debugger.
    Press 'c' to continue running code.
    """
    import ipdb  # noqa - don't import at top level in case not installed

    # Switch off unwanted IPython loggers
    for lib in ('asyncio', 'parso'):
        logging.getLogger(lib).setLevel(logging.WARNING)

    pyqtRemoveInputHook()
    ipdb.set_trace()
