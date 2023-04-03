"""
Module for utilities and functions to help with development.
"""
import logging

from PyQt5.QtCore import pyqtRemoveInputHook


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
