"""
Tests for functions in the transformation module
"""
import pytest

import numpy as np

from csv import DictReader
from pathlib import Path

from tactool.main import TACtool
from tactool.analysis_point import (
    affine_transform_point,
    affine_transform_matrix,
)

X_PLUS_10 = np.array([[1, 0, 10],
                      [0, 1, 0],
                      [0, 0, 1]])

Y_PLUS_10 = np.array([[1, 0, 0],
                      [0, 1, 10],
                      [0, 0, 1]])

SCALE_BY_2ish = np.array([[2.1, 0, 0],
                          [0, 2.1, 0],
                          [0, 0, 1]])


@pytest.mark.parametrize('matrix, src, expected', [
    (X_PLUS_10, (1, 1), (11, 1)),
    (X_PLUS_10, (1, 0), (11, 0)),
    (X_PLUS_10, (0, 1), (10, 1)),
    (Y_PLUS_10, (1, 1), (1, 11)),
    (Y_PLUS_10, (1, 0), (1, 10)),
    (Y_PLUS_10, (0, 1), (0, 11)),
    (SCALE_BY_2ish, (1, 1), (2, 2)),  # should round to nearest int
    (SCALE_BY_2ish, (10, 10), (21, 21)),  # no rounding required
])
def test_affine_transform_point(matrix, src, expected):
    # Act
    transformed = affine_transform_point(matrix, src)

    # Assert
    assert transformed == expected


def test_affine_transform_matrix():
    # Arrange
    src = [(0, 0), (1, 0), (1, 1), (0, 1)]
    dest = [(2, 2), (3, 2), (3, 3), (2, 3)]
    expected = np.array([
        [1, 0, 2],
        [0, 1, 2],
        [0, 0, 1]
    ])

    # Act
    matrix = affine_transform_matrix(src, dest)

    # Assert
    np.testing.assert_array_almost_equal(matrix, expected, decimal=10)


def test_recoordinate_sem_points(tmp_path: Path, tactool: TACtool):
    # Arrange
    input_csv = "test/data/analysis_points_complete.csv"
    output_csv = tmp_path / "analysis_points_complete.csv"
    # Place 3 Analysis Points which will be used for recoordination
    tactool.graphics_view.left_click.emit(336, 472)
    tactool.graphics_view.left_click.emit(318, 394)
    tactool.graphics_view.left_click.emit(268, 469)
    # Toggle recoordinate dialog so that the recoordinate_dialog is callable
    tactool.window.toggle_recoordinate_dialog()
    expected_coordinates = [
        (336, 472),
        (318, 394),
        (268, 469),
        (340, 527),
        (380, 362),
    ]

    # Act
    tactool.recoordinate_dialog.recoordinate_sem_points(
        input_csv, output_csv,
        x_header="X", y_header="Y", ref_col="Type", ref_label="RefMark",
    )

    # Assert
    with open(input_csv) as input_file, open(output_csv) as output_file:
        input_reader = DictReader(input_file)
        output_reader = DictReader(output_file)

        # Check that the headers remain the same
        assert input_reader.fieldnames == output_reader.fieldnames

        non_coord_headers = ["Name", "Type", "diameter", "scale", "colour", "mount_name", "material", "notes"]

        # Iterate through CSV file lines
        for input_item, output_item, (new_x, new_y) in zip(input_reader, output_reader, expected_coordinates):
            # Check that the non coordinate fields remain the same
            for header in non_coord_headers:
                assert input_item[header] == output_item[header]
            # Check that the coordinate fields are correct
            assert int(output_item["X"]) == new_x
            assert int(output_item["Y"]) == new_y
