"""
Tests for classes and functions within model.py

qapp fixture starts a running QApplication for the context of the test.
"""
import pytest

from tactool.analysis_point import AnalysisPoint
from tactool.table_model import TableModel


@pytest.mark.parametrize("expected_data, match_status", [
    (AnalysisPoint(
        1, "RefMark", 123, 456, 10, 1.0, "#ffff00", "sample_x67", "mount_x15", "duck", "note1", None, None, None),
        True),
    (AnalysisPoint(
        2, "RefMark", 123, 456, 10, 1.0, "#ffff00", "", "mount_x15", "", "note1", None, None, None),
        False),
    (AnalysisPoint(
        1, "RefMark", 222, 456, 10, 1.0, "#ffff00", "sample_x67", "mount_x81", "duck", "note1", None, None, None),
        False),
    (AnalysisPoint(
        1, "RefMark", 123, 222, 10, 1.0, "#ffff00", "", "", "", "note1", None, None, None),
        False),
    (AnalysisPoint(
        1, "222", 123, 456, 10, 1.0, "#ffff00", "sample_x83", "mount_x15", "duck", "note1", None, None, None),
        False),
    (AnalysisPoint(
        1, "RefMark", 123, 456, 222, 1.0, "#ffff00", "sample_x67", "mount_x15", "", "note1", None, None, None),
        False),
    (AnalysisPoint(
        1, "RefMark", 123, 456, 10, 1.0, "#22222", "", "", "duck", "note1", None, None, None),
        False),
    (AnalysisPoint(
        1, "RefMark", 123, 456, 10, 1.0, "#ffff00", "sample_x67", "mount_x15", "", "222", None, None, None),
        False),
    (AnalysisPoint(
        1, "RefMark", 123, 456, 10, 1.0, "#ffff00", "sample_x67", "mount_x15", "duck", "note1", 222, None, None),
        True),
    (AnalysisPoint(
        1, "RefMark", 123, 456, 10, 1.0, "#ffff00", "sample_x67", "mount_x15", "duck", "note1", None, 222, None),
        True),
    (AnalysisPoint(
        1, "RefMark", 123, 456, 10, 1.0, "#ffff00", "sample_x67", "mount_x15", "duck", "note1", None, None, 222),
        True),
]
)
def test_analysis_point_public_attributes_match(
    public_index: int,
    expected_data: AnalysisPoint,
    match_status: bool,
):
    """
    Function to test the functionality of comparing Analysis Point public attributes.
    For this, only the public attributes must match the existing Analysis Point.
    """
    analysis_point = AnalysisPoint(1, "RefMark", 123, 456, 10, 1.0, "#ffff00", "sample_x67", "mount_x15",
                                   "duck", "note1", None, None, None)
    # Compare just the public attributes of the points, i.e. up to the last 3
    assert (analysis_point.aslist()[:public_index] == expected_data.aslist()[:public_index]) is match_status


def test_model(model: TableModel):
    """
    Function to test the functionality of the PyQt Table Model of TACtool.
    """
    expected_data = [
        [1, "RefMark", 123, 456, 10, 1.0, "#ffff00", "sample_x83", "mount_x15",
         "rock", "note1", "outer_ellipse1", "inner_ellipse1", "label_item1"],
        [2, "RefMark", 123, 456, 10, 1.0, "#ffff00", "sample_x67", "mount_x81",
         "rock", "note2", "outer_ellipse2", "inner_ellipse2", "label_item2"],
        [3, "Spot", 123, 456, 10, 1.0, "#ffff00", "sample_x67", "mount_x15",
         "duck", "note3", "outer_ellipse3", "inner_ellipse3", "label_item3"]
    ]

    # Check that the PyQt Table Model is empty with the correct headers
    assert model._data == []
    assert model.headers == [
        "id",
        "label",
        "x",
        "y",
        "diameter",
        "scale",
        "colour",
        "sample_name",
        "mount_name",
        "material",
        "notes",
        "_outer_ellipse",
        "_inner_ellipse",
        "_label_text_item",
    ]
    assert model.next_point_id == 1

    # Add Analysis Points to the PyQt Table Model and check that it has added correctly
    for row in expected_data:
        model.add_point(AnalysisPoint(*row))
    assert model._data == expected_data
    assert model.next_point_id == 4

    # Check that the PyQt Table Model does not return non existent Analysis Points
    assert model.get_point_by_ellipse("non-existent ellipse") is None
    assert model.get_point_by_apid(4) is None

    # Check that the PyQt Table Model does return the correct Analysis Point using the Point's ellipse
    analysis_point_2 = model.get_point_by_ellipse("outer_ellipse2")
    assert analysis_point_2 == AnalysisPoint(2, "RefMark", 123, 456, 10, 1.0, "#ffff00", "sample_x67", "mount_x81",
                                             "rock", "note2", "outer_ellipse2", "inner_ellipse2", "label_item2")

    # Check that the PyQt Table Model does not change the data when removing a non existent Analysis Point
    model.remove_point(4)
    assert model._data == expected_data
    assert model.next_point_id == 4

    # Check that the PyQt Table Model does remove the correct Analysis Point
    model.remove_point(1)
    assert model._data == expected_data[1:]
    assert model.next_point_id == 4

    # Check that the PyQt Table Model does return the correct Analysis Point using the Point's ID value
    analysis_point_3 = model.get_point_by_apid(3)
    assert analysis_point_3 == AnalysisPoint(3, "Spot", 123, 456, 10, 1.0, "#ffff00", "sample_x67", "mount_x15",
                                             "duck", "note3", "outer_ellipse3", "inner_ellipse3", "label_item3")

    # Check that the PyQt Table Model does remove the correct Analysis Point
    model.remove_point(3)
    assert model._data == expected_data[1:2]
    assert model.next_point_id == 3
