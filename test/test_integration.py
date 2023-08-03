"""
Integration tests to confirm that classes interact correctly.

It tests the connection of signals and slots by emitting signals to trigger changes and simulating button clicks.
Analysis Points are added and removed by emitting corresponding click signals.

tactool fixtures start a running QApplication for the context of the test.
"""
from tactool.main import TACtool
from tactool.analysis_point import AnalysisPoint


def test_add_and_remove_points(tactool: TACtool, public_index: int):
    """
    Function to test the functionality of adding and removing Analysis Points via mouse clicks.
    """
    # Test for empty model (ensures no leakage between apc fixtures)
    assert tactool.table_model.analysis_points == []

    # This is the width of the pen used to create the _outer_ellipse item to be added to the
    # diameter to assert if the ellipse was created to the correct size as the bounding box includes pen width
    offset = 4

    # The 1st Analysis Point has default settings
    tactool.graphics_view.left_click.emit(101, 101)

    # Adjust the settings for the 2nd Analysis Point
    tactool.window.update_point_settings(
        sample_name="sample_x83",
        mount_name="mount_x81",
        material="rock",
        label="Spot",
        diameter=50,
        scale=2.0,
        colour="#222222",
    )
    tactool.graphics_view.left_click.emit(202, 202)

    # Adjust the settings for the 3rd Analysis Point
    # Purposefully making it overlap the 2nd Analysis Point
    tactool.window.update_point_settings(
        sample_name="sample_x67",
        mount_name="mount_x15",
        material="duck",
        label="RefMark",
        colour="#333333",
    )
    tactool.graphics_view.left_click.emit(240, 240)

    expected_data = [
        AnalysisPoint(1, "RefMark", 101, 101, 10, 1.0, "#ffff00", "", "", "", "", None, None, None),
        AnalysisPoint(2, "Spot", 202, 202, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", "", None, None, None),
        AnalysisPoint(3, "RefMark", 240, 240, 50, 2.0, "#333333", "sample_x67", "mount_x15",
                      "duck", "", None, None, None),
    ]
    # Iterate through each actual Analysis Point and compare to expected Analysis Point
    for index, analysis_point in enumerate(tactool.table_model.analysis_points):
        # Using list slicing to compare just the public attributes of the Analysis Points, i.e. up to the last 3
        assert analysis_point.aslist()[:public_index] == expected_data[index].aslist()[:public_index]
        # Compare the size of the actual ellipse to the mathematically expected size
        expected_ellipse = (expected_data[index].diameter * expected_data[index].scale) + offset
        assert analysis_point._outer_ellipse.boundingRect().width() == expected_ellipse

    # Remove the Analysis Point with an ID value of 3
    # Purposefully clicking between the 2nd and 3rd point to ensure the 3rd one is still deleted
    # It should work like a stack when deleting overlapping points
    tactool.graphics_view.right_click.emit(221, 221)

    # Right click on an empty part of the PyQt Graphics View
    # Nothing should change
    tactool.graphics_view.right_click.emit(0, 0)

    # Adjust the settings for the 4th Analysis Point to match those of the 2nd Analysis Point
    # This is done by emitting a signal from the PyQt Table View of the selected Analysis Point
    tactool.table_view.selected_analysis_point.emit(expected_data[1], 0)
    # The 4th Analysis Point ID value should be 3
    tactool.graphics_view.left_click.emit(404, 404)

    expected_data = [
        AnalysisPoint(1, "RefMark", 101, 101, 10, 1.0, "#ffff00", "", "", "", "", None, None, None),
        AnalysisPoint(2, "Spot", 202, 202, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", "", None, None, None),
        AnalysisPoint(3, "Spot", 404, 404, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", "", None, None, None),
    ]
    # Iterate through each actual Analysis Point and compare to expected Analysis Point
    for index, analysis_point in enumerate(tactool.table_model.analysis_points):
        # Using list slicing to compare just the public attributes of the Analysis Points, i.e. up to the last 3
        assert analysis_point.aslist()[:public_index] == expected_data[index].aslist()[:public_index]
        # Compare the size of the actual ellipse to the mathematically expected size
        expected_ellipse = (expected_data[index].diameter * expected_data[index].scale) + offset
        assert analysis_point._outer_ellipse.boundingRect().width() == expected_ellipse


def test_clear_points(tactool: TACtool):
    """
    Function to test the functionality of the Clear Points button.
    Some points are purposefully overlapping for the test.
    """
    # Check that the PyQt Table Model data is empty
    assert tactool.table_model.analysis_points == []

    # Add some Analysis Points
    tactool.graphics_view.left_click.emit(101, 101)
    tactool.graphics_view.left_click.emit(202, 202)
    tactool.graphics_view.left_click.emit(303, 303)
    # The 5th point partially overlaps the 4th point
    # This is intentional as this used to cause issues
    tactool.window.update_point_settings(
        sample_name="sample_x83",
        mount_name="mount_x81",
        material="rock",
        label="Spot",
        diameter=100,
        colour="#ff0000",
    )
    tactool.graphics_view.left_click.emit(404, 404)
    tactool.graphics_view.left_click.emit(440, 440)

    # Simulate a button click of the Clear Points button
    tactool.window.clear_points_button.click()

    # Check that all Analysis Points have been removed
    assert tactool.table_model.analysis_points == []


def test_reset_id_values(tactool: TACtool):
    """
    Function to test the functionality of the Reset IDs button.
    """
    # Add some Analysis Points
    tactool.graphics_view.left_click.emit(101, 101)
    tactool.graphics_view.left_click.emit(202, 202)
    tactool.graphics_view.left_click.emit(303, 303)
    tactool.graphics_view.left_click.emit(404, 404)
    tactool.graphics_view.left_click.emit(505, 505)

    # Remove the 1st and 4th Analysis Points
    # This will make the ID values go 2, 3, 5
    tactool.graphics_view.right_click.emit(101, 101)
    tactool.graphics_view.right_click.emit(404, 404)

    # Simulate a button click of the Reset IDs button
    tactool.window.reset_ids_button.click()

    # Iterate through each actual Analysis Point
    for current_id, analysis_point in enumerate(tactool.table_model.analysis_points):
        # Check that the ID value is equal to expected
        # We calculate expected ID value using the index of the Analysis Point in the Table Model
        assert analysis_point.id == current_id + 1


def test_reset_settings(tactool: TACtool):
    """
    Function to test the functionality of the Reset Settings button.
    """
    # Adjust the settings
    tactool.window.update_point_settings(
        sample_name="sample_x83",
        mount_name="mount_x81",
        material="rock",
        label="Spot",
        diameter=50,
        scale=2.0,
        colour="#222222",
    )

    # Simulate a button click of the Reset Settings button
    tactool.window.reset_settings_button.click()

    # Add some points, these should now have the default settings and metadata
    tactool.graphics_view.left_click.emit(101, 101)
    tactool.graphics_view.left_click.emit(202, 202)
    tactool.graphics_view.left_click.emit(303, 303)

    expected_settings = [
        tactool.window.default_settings["label"],
        tactool.window.default_settings["diameter"],
        float(tactool.window.default_settings["scale"]),
        tactool.window.default_settings["colour"],
        tactool.window.default_settings["metadata"],
        tactool.window.default_settings["metadata"],
        tactool.window.default_settings["metadata"],
    ]

    # Iterate through each actual Analysis Point
    for analysis_point in tactool.table_model.analysis_points:
        actual_settings = [
            analysis_point.label,
            analysis_point.diameter,
            analysis_point.scale,
            analysis_point.colour,
            analysis_point.sample_name,
            analysis_point.mount_name,
            analysis_point.material,
        ]
        assert actual_settings == expected_settings


def test_reference_point_hint(tactool: TACtool):
    """
    Function to test the functionality of the RefMark Points reminder in the Status Bar.
    """
    # Check reference Points hint is visible
    ref_points_status = tactool.window.status_bar_messages["ref_points"]["status"]
    assert ref_points_status is not None
    assert ref_points_status in tactool.window.status_bar.children()

    # Add 3 analysis points with the label 'RefMark'
    tactool.window.label_input.setCurrentText("RefMark")
    tactool.graphics_view.left_click.emit(100, 100)
    tactool.graphics_view.left_click.emit(150, 150)
    tactool.graphics_view.left_click.emit(200, 200)

    # Check reference Points hint not is visible
    ref_points_status = tactool.window.status_bar_messages["ref_points"]["status"]
    assert ref_points_status is None
    assert ref_points_status not in tactool.window.status_bar.children()

    # Remove 1 Analysis Point with label 'RefMark', bringing the total to 2 reference Points
    tactool.graphics_view.right_click.emit(100, 100)

    # Check reference Points hint is visible
    ref_points_status = tactool.window.status_bar_messages["ref_points"]["status"]
    assert ref_points_status is not None
    assert ref_points_status in tactool.window.status_bar.children()

    # Add 1 Analysis Point with label 'Spot', keeping the total at 2 reference Points
    tactool.window.label_input.setCurrentText("Spot")
    tactool.graphics_view.left_click.emit(100, 100)

    # Check reference Points hint is visible
    ref_points_status = tactool.window.status_bar_messages["ref_points"]["status"]
    assert ref_points_status is not None
    assert ref_points_status in tactool.window.status_bar.children()
