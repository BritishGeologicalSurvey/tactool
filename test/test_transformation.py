"""
Tests for functions in the transformation module
"""
import numpy as np
from typing import Any

import pytest

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


def test_toggle_recoordinate_dialog(tactool: TACtool, monkeypatch_qmsgbox_question_yes: pytest.MonkeyPatch):
    # Check that the RecoordinateDialog does not exist
    assert tactool.window.recoordinate_dialog is None
    # Check that the main input widgets are enabled
    for widget in tactool.window.main_input_widgets:
        assert widget.isEnabled() is True
    assert tactool.graphics_view.disable_analysis_points is False
    assert tactool.graphics_scene.transparent_window is None

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
    assert tactool.graphics_scene.transparent_window is None

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
    assert tactool.graphics_scene.transparent_window is not None

    # Close the RecoordinateDialog
    tactool.recoordinate_dialog.cancel_button.click()

    # Check that the RecoordinateDialog does not exist
    assert tactool.window.recoordinate_dialog is None
    # Check that the main input widgets are enabled
    for widget in tactool.window.main_input_widgets:
        assert widget.isEnabled() is True
    assert tactool.graphics_view.disable_analysis_points is False
    assert tactool.graphics_scene.transparent_window is None


@pytest.mark.parametrize(
    ["input_csv", "expected_points_data"],
    [
        (
            "test/data/SEM_co-ordinate_import_test_set.csv",
            [
                [1, "RefMark", 336, 472, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", ""],
                [2, "RefMark", 318, 394, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", ""],
                [3, "RefMark", 268, 469, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", ""],
                [509, "Spot", 271, 458, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", ""],
                [577, "Spot", 287, 483, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", ""],
                [662, "Spot", 309, 466, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", ""],
                [705, "Spot", 320, 458, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", ""],
                [759, "Spot", 332, 477, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", ""],
            ],
        ),
        (
            "test/data/SEM_co-ordinate_import_test_set_4_refs.csv",
            [
                [1, "RefMark", 336, 472, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", ""],
                [2, "RefMark", 318, 394, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", ""],
                [3, "RefMark", 268, 469, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", ""],
                [4, "RefMark", 324, 447, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", ""],
                [509, "Spot", 271, 458, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", ""],
                [577, "Spot", 287, 483, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", ""],
                [662, "Spot", 309, 466, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", ""],
                [705, "Spot", 320, 458, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", ""],
                [759, "Spot", 332, 477, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", ""],
            ],
        ),
    ],
)
def test_import_and_recoordinate_sem_csv(
    tactool: TACtool,
    public_index: int,
    input_csv: str,
    expected_points_data: list[list[Any]],
):
    # Arrange
    # Place 4 Analysis Points which will be used for recoordination
    # Only the first 3 should be used
    tactool.graphics_view.left_click.emit(336, 472)
    tactool.graphics_view.left_click.emit(318, 394)
    tactool.graphics_view.left_click.emit(268, 469)
    tactool.graphics_view.left_click.emit(87, 392)
    # Modify the Analysis Point settings as these should be applied to the recoordinated points
    tactool.window.update_point_settings(
        sample_name="sample_x83",
        mount_name="mount_x81",
        material="rock",
        label="Spot",
        diameter=50,
        scale=2.0,
        colour="#222222",
    )

    # Act
    # Toggle recoordinate dialog so that the recoordinate_dialog is callable
    tactool.window.toggle_recoordinate_dialog()
    tactool.recoordinate_dialog.input_csv_filepath_label.setText(input_csv)
    tactool.recoordinate_dialog.import_and_recoordinate_sem_csv()

    # Assert
    for expected_point, actual_point in zip(expected_points_data, tactool.table_model.analysis_points):
        assert expected_point == actual_point.aslist()[:public_index]
