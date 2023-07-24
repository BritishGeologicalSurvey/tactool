"""
Integration tests to confirm that classes interact correctly.

It tests the connection of signals and slots by emitting signals to trigger changes and simulating button clicks.
Analysis Points are added and removed by emitting corresponding click signals.

tactool fixtures start a running QApplication for the context of the test.
"""
from pathlib import WindowsPath

import pytest
from PyQt5.QtGui import QPixmap
from tactool.main import TACtool
from tactool.table_model import AnalysisPoint


PUBLIC_INDEX = len(TACtool([], testing_mode=True).window.table_model.headers) - 3


def test_add_and_remove_points(tactool: TACtool) -> None:
    """
    Function to test the functionality of adding and removing Analysis Points via mouse clicks.
    """
    # Test for empty model (ensures no leakage between apc fixtures)
    assert tactool.window.table_model.analysis_points == []

    # This is the width of the pen used to create the _outer_ellipse item to be added to the
    # diameter to assert if the ellipse was created to the correct size as the bounding box includes pen width
    offset = 4

    # The 1st Analysis Point has default settings
    tactool.window.graphics_view.left_click.emit(101, 101)

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
    tactool.window.graphics_view.left_click.emit(202, 202)

    # Adjust the settings for the 3rd Analysis Point
    # Purposefully making it overlap the 2nd Analysis Point
    tactool.window.update_point_settings(
        sample_name="sample_x67",
        mount_name="mount_x15",
        material="duck",
        label="RefMark",
        colour="#333333",
    )
    tactool.window.graphics_view.left_click.emit(240, 240)

    expected_data = [
        AnalysisPoint(1, "RefMark", 101, 101, 10, 1.0, "#ffff00", "", "", "", "", None, None, None),
        AnalysisPoint(2, "Spot", 202, 202, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", "", None, None, None),
        AnalysisPoint(3, "RefMark", 240, 240, 50, 2.0, "#333333", "sample_x67", "mount_x15",
                      "duck", "", None, None, None),
    ]
    # Iterate through each actual Analysis Point and compare to expected Analysis Point
    for index, analysis_point in enumerate(tactool.window.table_model.analysis_points):
        # Using list slicing to compare just the public attributes of the Analysis Points, i.e. up to the last 3
        assert analysis_point.aslist()[:PUBLIC_INDEX] == expected_data[index].aslist()[:PUBLIC_INDEX]
        # Compare the size of the actual ellipse to the mathematically expected size
        expected_ellipse = (expected_data[index].diameter * expected_data[index].scale) + offset
        assert analysis_point._outer_ellipse.boundingRect().width() == expected_ellipse

    # Remove the Analysis Point with an ID value of 3
    # Purposefully clicking between the 2nd and 3rd point to ensure the 3rd one is still deleted
    # It should work like a stack when deleting overlapping points
    tactool.window.graphics_view.right_click.emit(221, 221)

    # Right click on an empty part of the PyQt Graphics View
    # Nothing should change
    tactool.window.graphics_view.right_click.emit(0, 0)

    # Adjust the settings for the 4th Analysis Point to match those of the 2nd Analysis Point
    # This is done by emitting a signal from the PyQt Table View of the selected Analysis Point
    tactool.window.table_view.selected_analysis_point.emit(expected_data[1], 0)
    # The 4th Analysis Point ID value should be 3
    tactool.window.graphics_view.left_click.emit(404, 404)

    expected_data = [
        AnalysisPoint(1, "RefMark", 101, 101, 10, 1.0, "#ffff00", "", "", "", "", None, None, None),
        AnalysisPoint(2, "Spot", 202, 202, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", "", None, None, None),
        AnalysisPoint(3, "Spot", 404, 404, 50, 2.0, "#222222", "sample_x83", "mount_x81", "rock", "", None, None, None),
    ]
    # Iterate through each actual Analysis Point and compare to expected Analysis Point
    for index, analysis_point in enumerate(tactool.window.table_model.analysis_points):
        # Using list slicing to compare just the public attributes of the Analysis Points, i.e. up to the last 3
        assert analysis_point.aslist()[:PUBLIC_INDEX] == expected_data[index].aslist()[:PUBLIC_INDEX]
        # Compare the size of the actual ellipse to the mathematically expected size
        expected_ellipse = (expected_data[index].diameter * expected_data[index].scale) + offset
        assert analysis_point._outer_ellipse.boundingRect().width() == expected_ellipse


def test_clear_points(tactool: TACtool) -> None:
    """
    Function to test the functionality of the Clear Points button.
    Some points are purposefully overlapping for the test.
    """
    # Check that the PyQt Table Model data is empty
    assert tactool.window.table_model.analysis_points == []

    # Add some Analysis Points
    tactool.window.graphics_view.left_click.emit(101, 101)
    tactool.window.graphics_view.left_click.emit(202, 202)
    tactool.window.graphics_view.left_click.emit(303, 303)
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
    tactool.window.graphics_view.left_click.emit(404, 404)
    tactool.window.graphics_view.left_click.emit(440, 440)

    # Simulate a button click of the Clear Points button
    tactool.window.clear_points_button.click()

    # Check that all Analysis Points have been removed
    assert tactool.window.table_model.analysis_points == []


def test_reset_id_values(tactool: TACtool) -> None:
    """
    Function to test the functionality of the Reset IDs button.
    """
    # Add some Analysis Points
    tactool.window.graphics_view.left_click.emit(101, 101)
    tactool.window.graphics_view.left_click.emit(202, 202)
    tactool.window.graphics_view.left_click.emit(303, 303)
    tactool.window.graphics_view.left_click.emit(404, 404)
    tactool.window.graphics_view.left_click.emit(505, 505)

    # Remove the 1st and 4th Analysis Points
    # This will make the ID values go 2, 3, 5
    tactool.window.graphics_view.right_click.emit(101, 101)
    tactool.window.graphics_view.right_click.emit(404, 404)

    # Simulate a button click of the Reset IDs button
    tactool.window.reset_ids_button.click()

    # Iterate through each actual Analysis Point
    for current_id, analysis_point in enumerate(tactool.window.table_model.analysis_points):
        # Check that the ID value is equal to expected
        # We calculate expected ID value using the index of the Analysis Point in the Table Model
        assert analysis_point.id == current_id + 1


def test_reset_settings(tactool: TACtool) -> None:
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
    tactool.window.graphics_view.left_click.emit(101, 101)
    tactool.window.graphics_view.left_click.emit(202, 202)
    tactool.window.graphics_view.left_click.emit(303, 303)

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
    for analysis_point in tactool.window.table_model.analysis_points:
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


def test_toggle_scaling_mode(tactool: TACtool) -> None:
    """
    Function to test the functionality of the scaling mode.
    """
    # Check that the SetScaleDialog and the transparent rectangle
    # on the PyQt Graphics Scene do not exist
    assert tactool.window.set_scale_dialog is None
    assert tactool.window.graphics_scene.scaling_rect is None
    # Check that the main input widgets are enabled
    for widget in tactool.window.main_input_widgets:
        assert widget.isEnabled() is True
    assert tactool.window.graphics_view.disable_analysis_points is False

    # Start the scaling mode
    tactool.window.toggle_scaling_mode()

    # Check that the SetScaleDialog and the transparent rectangle
    # on the PyQt Graphics Scene exist and are the correct type
    assert tactool.window.set_scale_dialog is not None
    assert tactool.window.graphics_scene.scaling_rect is not None
    # Check that the main input widgets are disabled
    for widget in tactool.window.main_input_widgets:
        assert widget.isEnabled() is False
    assert tactool.window.graphics_view.disable_analysis_points is True

    # Set the scale, following the same steps as the user would
    tactool.window.set_scale_dialog.scale_value.setText(str(2.0))
    tactool.window.set_scale_dialog.set_scale()

    # Check that the SetScaleDialog and the transparent rectangle
    # on the PyQt Graphics Scene do not exist
    assert tactool.window.set_scale_dialog is None
    assert tactool.window.graphics_scene.scaling_rect is None
    # Check that the main input widgets are enabled
    for widget in tactool.window.main_input_widgets:
        assert widget.isEnabled() is True
    assert tactool.window.graphics_view.disable_analysis_points is False


def test_set_scale(tactool: TACtool) -> None:
    """
    Function to test the functionality of setting the scale.
    """
    # Set the scale, following the same steps as the user would
    scale = 2.0
    tactool.window.toggle_scaling_mode()
    tactool.window.set_scale_dialog.scale_value.setText(str(scale))
    tactool.window.set_scale_dialog.set_scale()

    # Add some points, these should now have the new scale
    tactool.window.graphics_view.left_click.emit(101, 101)
    tactool.window.graphics_view.left_click.emit(202, 202)
    tactool.window.graphics_view.left_click.emit(303, 303)

    # Iterate through each actual Analysis Point
    for analysis_point in tactool.window.table_model.analysis_points:
        # Check that the scale value is equal to expected
        assert analysis_point.scale == scale


def test_export_image(tactool: TACtool, tmp_path: WindowsPath) -> None:
    """
    Function to test the functionality of exporting an image.
    """
    tmp_image_path = tmp_path / "exported_image.png"

    # Add some Analysis Points
    tactool.window.graphics_view.left_click.emit(101, 101)
    tactool.window.graphics_view.left_click.emit(202, 202)
    tactool.window.graphics_view.left_click.emit(303, 303)
    tactool.window.update_point_settings(
        sample_name="sample_x83",
        mount_name="mount_x81",
        material="rock",
        label="Spot",
        diameter=100,
        colour="#ff0000",
    )
    tactool.window.graphics_view.left_click.emit(404, 404)
    # The 5th point purposefully goes over the imported image border
    tactool.window.graphics_view.left_click.emit(555, 555)

    # Zoom in on the PyQt Graphics View
    factor = 1.25
    tactool.window.graphics_view._zoom += 1
    tactool.window.graphics_view.scale(factor, factor)

    # Save the image to the given filepath
    tactool.window.graphics_view.save_image(str(tmp_image_path))

    # Check that the filepath and the newly saved file exist
    assert tmp_image_path.exists()
    assert tmp_image_path.is_file()

    # Load the newly created file and the expected image file into a PyQt5 Pixmap
    # This allows us to use already imported modules to compare the image sizes
    actual_image = QPixmap(str(tmp_image_path))
    expected_image = QPixmap("test/data/exported_image.png")
    assert actual_image.size() == expected_image.size()


@pytest.mark.parametrize("filepath, expected_points", [
    ("test/data/analysis_points_complete.csv", [
        AnalysisPoint(1, "RefMark", 472, 336, 10, 1.0, "#ffff00", "sample_x83", "mount_x81", "rock",
                      "this point has padded zeros in the id column", None, None, None),
        AnalysisPoint(2, "RefMark", 394, 318, 10, 1.0, "#ffff00", "sample_x83", "mount_x81",
                      "rock", "", None, None, None),
        AnalysisPoint(3, "RefMark", 469, 268, 10, 1.0, "#ffff00", "sample_x83", "mount_x81",
                      "rock", "point3", None, None, None),
        AnalysisPoint(4, "Spot", 527, 340, 10, 1.0, "#204a87", "sample_x67", "mount_x15", "duck",
                      "point4 with whitespace, and comma", None, None, None),
        AnalysisPoint(5, "Spot", 362, 380, 15, 1.0, "#204a87", "sample_x67", "mount_x15", "duck",
                      "point5 with whitespace", None, None, None),
    ]),
    ("test/data/id_x_y_partial.csv", [
        AnalysisPoint(1, "RefMark", 295, 276, 10, 1.0, "#ffff00", "", "", "", "", None, None, None),
        AnalysisPoint(2, "RefMark", 386, 257, 10, 1.0, "#ffff00", "", "", "", "", None, None, None),
        AnalysisPoint(3, "RefMark", 334, 282, 10, 1.0, "#ffff00", "", "", "", "", None, None, None),
        AnalysisPoint(4, "RefMark", 357, 315, 10, 1.0, "#ffff00", "", "", "", "", None, None, None),
        AnalysisPoint(5, "RefMark", 327, 334, 10, 1.0, "#ffff00", "", "", "", "", None, None, None),
    ]),
    ("test/data/x_y_partial.csv", [
        AnalysisPoint(1, "Spot", 295, 276, 10, 1.0, "#ffff00", "", "", "rock", "", None, None, None),
        AnalysisPoint(2, "Spot", 386, 257, 10, 1.0, "#ffff00", "", "", "rock", "", None, None, None),
        AnalysisPoint(3, "Spot", 334, 282, 10, 1.0, "#ffff00", "", "", "rock", "", None, None, None),
        AnalysisPoint(4, "Spot", 357, 315, 10, 1.0, "#ffff00", "", "", "duck", "", None, None, None),
        AnalysisPoint(5, "Spot", 327, 334, 10, 1.0, "#ffff00", "", "", "duck", "", None, None, None),
    ]),
])
def test_import_tactool_csv(tactool: TACtool, filepath: str, expected_points: list[AnalysisPoint]) -> None:
    """
    Function to test the functionality of importing a TACtool CSV file.
    """
    # Check that the PyQt Table Model data is empty
    assert tactool.window.table_model.analysis_points == []

    # Set Analysis Point settings that are used where data is missing
    tactool.window.update_point_settings(
        sample_name="sample_x83",
        mount_name="mount_x81",
        material="rock",
        label="Spot",
        diameter=99,
        scale=1.0,
        colour="#999999",
    )

    # Import the data from the given TACtool CSV file
    tactool.window.load_tactool_csv_data(filepath)

    # Iterate through the actual Analysis Points created from the CSV file
    # and the calculated Analysis Points in this test
    for loaded_point, expected_point in zip(tactool.window.table_model.analysis_points, expected_points):
        # Using list slicing to compare just the public attributes of the Analysis Points, i.e. up to the last 3
        assert expected_point.aslist()[:PUBLIC_INDEX] == loaded_point.aslist()[:PUBLIC_INDEX]

    # Click new points
    tactool.window.graphics_view.left_click.emit(111, 111)

    # Check that the ID values continue from the maximum ID value in the CSV file
    assert len(tactool.window.table_model.analysis_points) == 6


def test_export_tactool_csv(tactool: TACtool, tmp_path: WindowsPath) -> None:
    """
    Function to test the functionality of exporting a TACtool CSV file.
    """
    # Check that the PyQt Table Model data is empty
    assert tactool.window.table_model.analysis_points == []

    csv_path = tmp_path / "test.csv"
    expected_headers = ["Name", "Type", "X", "Y", "Z", "diameter", "scale", "colour",
                        "mount_name", "material", "notes"]
    expected_data = [
        ["_#001", "RefMark", 101, 101, 0, 10, 1.0, "#ffff00", "", "", ""],
        ["_#002", "RefMark", 202, 202, 0, 10, 1.0, "#ffff00", "", "", ""],
        ["sample_x83_#003", "Spot", 303, 303, 0, 100, 1.5, "#444444", "mount_x81", "duck", ""],
    ]

    # Add 2 Analysis Points
    tactool.window.graphics_view.left_click.emit(101, 101)
    tactool.window.graphics_view.left_click.emit(202, 202)

    # Adjust the settings for the 3rd Analysis Point
    tactool.window.update_point_settings(
        sample_name="sample_x83",
        mount_name="mount_x81",
        material="duck",
        label="Spot",
        diameter=100,
        scale=1.5,
        colour="#444444",
    )
    tactool.window.graphics_view.left_click.emit(303, 303)

    # Save the data to the given CSV file path
    tactool.window.table_model.export_csv(csv_path)
    assert_csv_data(csv_path, expected_headers, expected_data)


def assert_csv_data(csv_path: str, expected_headers: list[str], expected_data: list) -> None:
    """
    Function to assert that the CSV data in the given file matches the given expected data.
    """
    with open(csv_path) as csv_file:
        # Check that the headers are correct
        actual_headers = [item.strip() for item in csv_file.readline().split(",")]
        assert actual_headers == expected_headers

        # Check that the Analysis Point data is correct
        lines = csv_file.readlines()
        # Iterate through the expected Analysis Point data
        for index, item in enumerate(expected_data):
            # Convert the CSV row into a list
            csv_row_data = [item.strip() for item in lines[index].split(",")]

            # Iterate through the CSV Analysis Points
            for item_attribute, csv_attribute in zip(item, csv_row_data):
                # Check that the attributes match
                # Attributes from the expected Analysis Point are converted to a string because
                # the raw CSV data will all be a string type
                assert csv_attribute == str(item_attribute)


def test_reference_point_hint(tactool: TACtool) -> None:
    """
    Function to test the functionality of the RefMark Points reminder in the Status Bar.
    """
    # Check reference Points hint is visible
    ref_points_status = tactool.window.status_bar_messages["ref_points"]["status"]
    assert ref_points_status is not None
    assert ref_points_status in tactool.window.status_bar.children()

    # Add 3 analysis points with the label 'RefMark'
    tactool.window.label_input.setCurrentText("RefMark")
    tactool.window.graphics_view.left_click.emit(100, 100)
    tactool.window.graphics_view.left_click.emit(150, 150)
    tactool.window.graphics_view.left_click.emit(200, 200)

    # Check reference Points hint not is visible
    ref_points_status = tactool.window.status_bar_messages["ref_points"]["status"]
    assert ref_points_status is None
    assert ref_points_status not in tactool.window.status_bar.children()

    # Remove 1 Analysis Point with label 'RefMark', bringing the total to 2 reference Points
    tactool.window.graphics_view.right_click.emit(100, 100)

    # Check reference Points hint is visible
    ref_points_status = tactool.window.status_bar_messages["ref_points"]["status"]
    assert ref_points_status is not None
    assert ref_points_status in tactool.window.status_bar.children()

    # Add 1 Analysis Point with label 'Spot', keeping the total at 2 reference Points
    tactool.window.label_input.setCurrentText("Spot")
    tactool.window.graphics_view.left_click.emit(100, 100)

    # Check reference Points hint is visible
    ref_points_status = tactool.window.status_bar_messages["ref_points"]["status"]
    assert ref_points_status is not None
    assert ref_points_status in tactool.window.status_bar.children()


def test_scale_hint(tactool: TACtool) -> None:
    """
    Function to test the functionality of the Set Scale reminder in the Status Bar.
    """
    # Check Set Scale hint is not visible
    set_scale_status = tactool.window.status_bar_messages["set_scale"]["status"]
    assert set_scale_status is None
    assert set_scale_status not in tactool.window.status_bar.children()

    # Add some points by clicking
    tactool.window.graphics_view.left_click.emit(101, 101)
    tactool.window.graphics_view.left_click.emit(202, 202)
    tactool.window.graphics_view.left_click.emit(303, 303)

    # Check Set Scale hint is visible
    set_scale_status = tactool.window.status_bar_messages["set_scale"]["status"]
    assert set_scale_status is not None
    assert set_scale_status in tactool.window.status_bar.children()

    # Set the scale, following the same steps as the user would
    tactool.window.toggle_scaling_mode()
    tactool.window.set_scale_dialog.scale_value.setText(str(2.0))
    tactool.window.set_scale_dialog.set_scale()

    # Check Set Scale hint is not visible
    set_scale_status = tactool.window.status_bar_messages["set_scale"]["status"]
    assert set_scale_status is None
    assert set_scale_status not in tactool.window.status_bar.children()

    # Reset the Scale value to the default value
    tactool.window.reset_settings()

    # Check Set Scale hint is visible
    set_scale_status = tactool.window.status_bar_messages["set_scale"]["status"]
    assert set_scale_status is not None
    assert set_scale_status in tactool.window.status_bar.children()
