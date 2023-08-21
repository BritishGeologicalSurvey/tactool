"""
Tests for functions in the transformation module
"""
import pytest

import numpy as np

from csv import DictReader
from pathlib import Path

from tactool.main import TACtool
from tactool.recoordinate_dialog import (
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


@pytest.mark.parametrize(
    ["matrix", "src", "expected"],
    [
        (X_PLUS_10, (1, 1), (11, 1)),
        (X_PLUS_10, (1, 0), (11, 0)),
        (X_PLUS_10, (0, 1), (10, 1)),
        (Y_PLUS_10, (1, 1), (1, 11)),
        (Y_PLUS_10, (1, 0), (1, 10)),
        (Y_PLUS_10, (0, 1), (0, 11)),
        (SCALE_BY_2ish, (1, 1), (2, 2)),  # should round to nearest int
        (SCALE_BY_2ish, (10, 10), (21, 21)),  # no rounding required
    ]
)
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


def test_toggle_recoordinate_dialog(tactool: TACtool):
    # close recoord window
    # check that toggling off works, main widgets, grey rect, disable graphics scene points

    # Check that the RecoordinateDialog does not exist
    assert tactool.window.recoordinate_dialog is None
    # Check that the main input widgets are enabled
    for widget in tactool.window.main_input_widgets:
        assert widget.isEnabled() is True
    assert tactool.graphics_view.disable_analysis_points is False
    assert tactool.graphics_scene.scaling_rect is None

    # Add 2 RefMark points
    tactool.graphics_view.left_click.emit(336, 472)
    tactool.graphics_view.left_click.emit(318, 394)

    # Try to start the recoordination dialog
    # This should not work because 3 RefMark points are needed
    # and currently there are only 2
    tactool.window.toggle_recoordinate_dialog()

    # Check that the RecoordinateDialog does not exist
    assert tactool.window.recoordinate_dialog is None
    # Check that the main input widgets are enabled
    for widget in tactool.window.main_input_widgets:
        assert widget.isEnabled() is True
    assert tactool.graphics_view.disable_analysis_points is False
    assert tactool.graphics_scene.scaling_rect is None

    # Add the 3rd RefMark point
    tactool.graphics_view.left_click.emit(268, 469)

    # Toggle the recoordinate dialog, this should now work
    tactool.window.toggle_recoordinate_dialog()

    # Check that the RecoordinateDialog does exist
    assert tactool.window.recoordinate_dialog is not None
    # Check that the main input widgets are disabled
    for widget in tactool.window.main_input_widgets:
        assert widget.isEnabled() is False
    assert tactool.graphics_view.disable_analysis_points is True
    assert tactool.graphics_scene.scaling_rect is not None

    # Close the RecoordinateDialog
    tactool.recoordinate_dialog.cancel_button.click()

    # Check that the RecoordinateDialog does not exist
    assert tactool.window.recoordinate_dialog is None
    # Check that the main input widgets are enabled
    for widget in tactool.window.main_input_widgets:
        assert widget.isEnabled() is True
    assert tactool.graphics_view.disable_analysis_points is False
    assert tactool.graphics_scene.scaling_rect is None


@pytest.mark.parametrize(
    ["input_csv", "expected_coordinates", "recoordinate_args", "non_coord_headers"],
    [
        (
            "test/data/analysis_points_complete.csv",
            [(336, 472), (318, 394), (268, 469), (340, 527), (380, 362)],
            {"invert_x_axis_dest": False, "x_header": "X", "y_header": "Y",
             "ref_col": "Type", "ref_label": "RefMark"},
            ["Name", "Type", "diameter", "scale", "colour", "mount_name", "material", "notes"],
        ),
        (
            "test/data/SEM_co-ordinate_import_test_set.csv",
            [(460, 472), (478, 394), (528, 469), (525, 458), (509, 483), (487, 466), (476, 458), (464, 477)],
            {"invert_x_axis_dest": True, "x_header": "Laser Ablation Centre X", "y_header": "Laser Ablation Centre Y",
             "ref_col": "Mineral Classification", "ref_label": "Fiducial"},
            ["Particle ID", "Mineral Classification", "Effective Diameter m",
             "Feret Max Diameter m", "Feret Min Diameter m", "F (N)", "Cl (N)"],
        ),
        (
            "test/data/SEM_co-ordinate_import_test_set_4_refs.csv",
            [(460, 472), (478, 394), (528, 469), (472, 447), (525, 458),
             (509, 483), (487, 466), (476, 458), (464, 477)],
            {"invert_x_axis_dest": True, "x_header": "Laser Ablation Centre X", "y_header": "Laser Ablation Centre Y",
             "ref_col": "Mineral Classification", "ref_label": "Fiducial"},
            ["Particle ID", "Mineral Classification", "Effective Diameter m",
             "Feret Max Diameter m", "Feret Min Diameter m", "F (N)", "Cl (N)"],
        ),
    ],
)
def test_recoordinate_sem_points(
    tmp_path: Path,
    tactool: TACtool,
    input_csv: str,
    expected_coordinates: list[tuple[int, int]],
    recoordinate_args: dict[str, str],
    non_coord_headers: list[str],
):
    # Arrange
    output_csv = tmp_path / "recoordinated_output.csv"
    print(output_csv)
    # Place 4 Analysis Points which will be used for recoordination
    # Only the first 3 should be used
    tactool.graphics_view.left_click.emit(336, 472)
    tactool.graphics_view.left_click.emit(318, 394)
    tactool.graphics_view.left_click.emit(268, 469)
    tactool.graphics_view.left_click.emit(87, 392)
    # Toggle recoordinate dialog so that the recoordinate_dialog is callable
    tactool.window.toggle_recoordinate_dialog()

    # Act
    tactool.recoordinate_dialog.recoordinate_sem_points(input_csv, output_csv, **recoordinate_args)

    # Assert
    with open(input_csv) as input_file, open(output_csv) as output_file:
        input_reader = DictReader(input_file)
        output_reader = DictReader(output_file)

        # Check that the headers remain the same
        assert input_reader.fieldnames == output_reader.fieldnames

        # Iterate through CSV file lines
        for input_item, output_item, (expect_x, expect_y) in zip(input_reader, output_reader, expected_coordinates):
            # Check that the non coordinate fields remain the same
            for header in non_coord_headers:
                assert input_item[header] == output_item[header]
            # Check that the coordinate fields are correct
            assert int(output_item[recoordinate_args["x_header"]]) == expect_x
            assert int(output_item[recoordinate_args["y_header"]]) == expect_y
