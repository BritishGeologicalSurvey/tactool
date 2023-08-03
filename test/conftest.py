"""
Definitions for test fixtures used within other tests.
"""
import pytest

from tactool.table_model import TableModel
from tactool.main import TACtool


@pytest.fixture(scope="function")
def tactool():
    """
    An instance of TACtool to use in tests.
    It depends on the tactool fixture, which is provided by pytest-qt and ensures that there is a
    running QApplication instance to allow Qt commands to work.
    """
    # Create an instance of the application in developer mode and testing mode
    tactool_application = TACtool([], developer_mode=True, debug_mode=True, testing_mode=True)

    yield tactool_application
    # Delete the application instance before restarting a new one
    del tactool_application


@pytest.fixture(scope="function")
def model():
    """
    An instance of the TableModel to be used in tests.
    """
    return TableModel()


@pytest.fixture(scope="function")
def public_index(model: TableModel):
    """
    The index in the list of headers where the public headers end.
    """
    return len(model.public_headers)
