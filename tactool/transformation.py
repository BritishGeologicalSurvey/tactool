"""
Functions for parsing TACtool CSV data and transformation existing Analysis Points.
"""
import numpy as np

from csv import DictReader
from typing import Any

from tactool.table_model import AnalysisPoint


def parse_tactool_csv(filepath: str, default_settings: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Parse the data in a given TACtool CSV file.
    """
    default_values = {
        "Name": 0,
        "X": 0,
        "Y": 0,
        "diameter": default_settings["diameter"],
        "scale": float(default_settings["scale"]),
        "colour": default_settings["colour"],
    }

    analysis_point_rows = []
    with open(filepath) as csv_file:
        reader = DictReader(csv_file)
        # Iterate through each line in the CSV file
        for id, item in enumerate(reader):

            # Split the id and sample_name value from the Name column
            if "_#" in item["Name"]:
                item["sample_name"], item["Name"] = item["Name"].rsplit("_#", maxsplit=1)

            # The default ID value is incremented with the row number
            default_values["Name"] = id + 1
            # If there is a Z column which is requried for the laser, then remove it
            try:
                item.pop("Z")
            except KeyError:
                pass

            item = parse_row_data(item, default_values)

            # Rename specific fields to match function arguments
            header_changes = {
                "Name": "apid",
                "X": "x",
                "Y": "y",
                "Type": "label",
            }
            for old_header, new_header in zip(header_changes, list(header_changes.values())):
                item[new_header] = item.pop(old_header)

            analysis_point_rows.append(item)
    return analysis_point_rows


def parse_row_data(item: dict, default_values: dict) -> dict:
    """
    Parse the data of an Analysis Point row item in a CSV file.
    """
    # Define the field names and their type conversions in Python
    fields = ["Name", "X", "Y", "diameter", "scale", "colour"]
    pre_processes = [int, int, int, int, float, None]

    # Iterate through each field, it's type conversion and it's default value
    for field, pre_process in zip(fields, pre_processes):
        try:
            # If a value has been given
            if item[field]:
                # If the value requires preprocessing
                if pre_process:
                    item[field] = pre_process(item[field])
            # Else when no value is given
            else:
                item[field] = default_values[field]
        # In the event of a KeyError, throw away the value which caused the error
        except KeyError:
            item[field] = default_values[field]
    return item


def reset_id(analysis_point: AnalysisPoint) -> AnalysisPoint:
    """
    Resed the ID value of a given Analysis Point.
    """
    analysis_point.id = None
    return analysis_point


"""
Notes on affine transformation:
An affine transformation converts one set of points into another via rotation,
skewing, scaling and translation.  It can be achieved mathematically by matrix
multiplication of a point vector by a transformation matrix.  It is slightly
complicated by the fact that a 2D transformation requires "homogeneous"
coordinates with 3 dimensions.  The transformation matrix can be calculated by
solving a linear equation involving the source and destination coordinate sets.
The following articles are helpful:
+ https://junfengzhang.com/2023/01/17/affine-transformation-why-3d-matrix-for-a-2d-transformation/
+ https://medium.com/hipster-color-science/computing-2d-affine-transformations-using-only-matrix-multiplication-2ccb31b52181  # noqa
"""


def affine_transform_matrix(
    source: list[tuple[float, float]],
    dest: list[tuple[float, float]],
) -> np.ndarray:
    # Convert the source and destination points to NumPy arrays
    source_array = np.array(source)
    dest_array = np.array(dest)

    # Add a column of ones to make the points homogeneous coordinates
    ones_column = np.ones((source_array.shape[0], 1))
    source_homogeneous = np.hstack((source_array, ones_column))
    dest_homogeneous = np.hstack((dest_array, ones_column))

    # Perform linear least squares regression to find the affine transformation matrix
    matrix, _, _, _ = np.linalg.lstsq(source_homogeneous, dest_homogeneous, rcond=None)

    return matrix.T


def affine_transform_point(
    matrix: np.ndarray,
    point: tuple[float, float],
) -> tuple[int, int]:
    """Apply an affine transformation to a 2D point"""
    # Convert the source point to 3D NumPy array
    # Adding z=1 makes point "homogeneous"
    src = np.array([*point, 1])

    # Apply the affine transformation
    dest = matrix @ src
    dest = (int(dest[0]), int(dest[1]))  # to 2D integer coordinate

    return dest
