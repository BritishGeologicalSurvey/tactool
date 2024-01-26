from pathlib import Path

import pytest
from PyQt5.QtGui import QPixmap

from tactool.main import TACtool
from tactool.analysis_point import (
    AnalysisPoint,
    export_tactool_csv,
    parse_sem_csv,
)


def test_export_image(tactool: TACtool, tmp_path: Path):
    tmp_image_path = tmp_path / "exported_image.png"

    # Add some Analysis Points
    tactool.graphics_view.left_click.emit(101, 101)
    tactool.graphics_view.left_click.emit(202, 202)
    tactool.graphics_view.left_click.emit(303, 303)
    tactool.window.update_point_settings(
        sample_name="sample_x83",
        mount_name="mount_x81",
        material="rock",
        label="Spot",
        diameter=100,
        colour="#ff0000",
    )
    tactool.graphics_view.left_click.emit(404, 404)
    # The 5th point purposefully goes over the imported image border
    tactool.graphics_view.left_click.emit(555, 555)

    # Zoom in on the PyQt Graphics View
    factor = 1.25
    tactool.graphics_view._zoom += 1
    tactool.graphics_view.scale(factor, factor)

    # Save the image to the given filepath
    tactool.graphics_view.save_image(str(tmp_image_path))

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
def test_import_tactool_csv(
    tactool: TACtool,
    public_index: int,
    filepath: str,
    expected_points: list[AnalysisPoint],
):
    # Check that the PyQt Table Model data is empty
    assert tactool.table_model.analysis_points == []

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
    for loaded_point, expected_point in zip(tactool.table_model.analysis_points, expected_points):
        # Using list slicing to compare just the public attributes of the Analysis Points, i.e. up to the last 3
        assert expected_point.aslist()[:public_index] == loaded_point.aslist()[:public_index]

    # Click new points
    tactool.graphics_view.left_click.emit(111, 111)

    # Check that the ID values continue from the maximum ID value in the CSV file
    assert len(tactool.table_model.analysis_points) == 6


def test_export_tactool_csv(tactool: TACtool, tmp_path: Path):
    # Check that the PyQt Table Model data is empty
    assert tactool.table_model.analysis_points == []

    csv_path = tmp_path / "test.csv"
    expected_headers = ["Name", "Type", "X", "Y", "Z", "diameter", "scale", "colour",
                        "mount_name", "material", "notes"]
    expected_data = [
        ["_#001", "RefMark", 101, 101, 0, 10, 1.0, "#ffff00", "", "", ""],
        ["_#002", "RefMark", 202, 202, 0, 10, 1.0, "#ffff00", "", "", ""],
        ["sample_x83_#003", "Spot", 303, 303, 0, 100, 1.5, "#444444", "mount_x81", "duck", ""],
    ]

    # Add 2 Analysis Points
    tactool.graphics_view.left_click.emit(101, 101)
    tactool.graphics_view.left_click.emit(202, 202)

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
    tactool.graphics_view.left_click.emit(303, 303)

    # Save the data to the given CSV file path
    export_tactool_csv(
        filepath=csv_path,
        headers=tactool.table_model.public_headers,
        analysis_points=tactool.table_model.analysis_points,
    )
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


def test_parse_sem_csv_good():
    # Arrange
    sem_csv = Path("test/data/SEM_co-ordinate_import_test_set.csv")
    expected_point_dicts = [
        {"label": "RefMark", "x": 91.576, "y": 67.762},
        {"label": "RefMark", "x": 86.01, "y": 55.893},
        {"label": "RefMark", "x": 98.138, "y": 49.417},
        {"apid": 509, "label": "Spot", "x": 96.764747, "y": 49.303754},
        {"apid": 577, "label": "Spot", "x": 97.520798, "y": 55.785059},
        {"apid": 662, "label": "Spot", "x": 93.746436, "y": 60.03264},
        {"apid": 705, "label": "Spot", "x": 91.770031, "y": 62.312733},
        {"apid": 759, "label": "Spot", "x": 92.415936, "y": 67.080603},
    ]

    # Act
    actual_point_dicts = parse_sem_csv(sem_csv)

    # Assert
    assert expected_point_dicts == actual_point_dicts


def test_parse_sem_csv_bad():
    # Arrange
    sem_csv = Path("test/data/analysis_points_complete.csv")
    expected_error = "SEM CSV missing required header: Particle ID"

    # Act
    with pytest.raises(KeyError) as excinfo:
        parse_sem_csv(sem_csv)

    # Assert
    assert expected_error in str(excinfo.value)
