"""
Functions for parsing TACtool CSV data and transformation existing Analysis Points.
"""

from csv import DictReader
from typing import Any

from tactool.table_model import AnalysisPoint


def parse_tactool_csv(filepath: str, default_settings = dict[str, Any]) -> list[dict[str, Any]]:
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
