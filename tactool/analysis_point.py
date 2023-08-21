"""
Includes the Analysis Point data class,
functions for parsing TACtool CSV data ready for Analysis Points,
functions for exporting current Analysis Points into a CSV format,
and functions for transformation of existing Analysis Points.
"""

import dataclasses
from csv import (
    DictReader,
    writer,
)
from typing import Any

from PyQt5.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsTextItem,
)


@dataclasses.dataclass
class AnalysisPoint:
    """
    Container class for encapsulating Analysis point data.
    """
    # Define the class variables for the Analysis Points
    id: int
    label: str
    x: int
    y: int
    diameter: int
    scale: float
    colour: str
    sample_name: str
    mount_name: str
    material: str
    notes: str
    _outer_ellipse: QGraphicsEllipseItem
    _inner_ellipse: QGraphicsEllipseItem
    _label_text_item: QGraphicsTextItem


    @classmethod
    def field_names(cls) -> list[str]:
        """
        Get the field names of the class object.
        """
        return [field.name for field in dataclasses.fields(cls)]


    def aslist(self) -> list[
        int,
        int,
        int,
        str,
        int,
        float,
        str,
        str,
        str,
        str,
        str,
        QGraphicsEllipseItem,
        QGraphicsEllipseItem,
        QGraphicsTextItem,
    ]:
        """
        Get the attributes of an Analysis Point object as a list.
        """
        attributes_list = [
            self.id,
            self.label,
            self.x,
            self.y,
            self.diameter,
            self.scale,
            self.colour,
            self.sample_name,
            self.mount_name,
            self.material,
            self.notes,
            self._outer_ellipse,
            self._inner_ellipse,
            self._label_text_item
        ]
        return attributes_list


def parse_tactool_csv(filepath: str, default_settings: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Parse the data in a given TACtool CSV file.
    """
    # Defining all header name changes, datatypes and default values
    fields = {
        "Name": {
            "new_header": "apid",
            "type": int,
            "default": 0,
        },
        "sample_name": {
            "new_header": "sample_name",
            "type": str,
            "default": "",
        },
        "Type": {
            "new_header": "label",
            "type": str,
            "default": "",
        },
        "X": {
            "new_header": "x",
            "type": int,
            "default": 0,
        },
        "Y": {
            "new_header": "y",
            "type": int,
            "default": 0,
        },
        "diameter": {
            "new_header": "diameter",
            "type": int,
            "default": default_settings["diameter"],
        },
        "scale": {
            "new_header": "scale",
            "type": float,
            "default": default_settings["scale"],
        },
        "colour": {
            "new_header": "colour",
            "type": str,
            "default": default_settings["colour"],
        },
        "mount_name": {
            "new_header": "mount_name",
            "type": str,
            "default": "",
        },
        "material": {
            "new_header": "material",
            "type": str,
            "default": "",
        },
        "notes": {
            "new_header": "notes",
            "type": str,
            "default": "",
        },
    }

    ap_dicts = []
    with open(filepath) as csv_file:
        reader = DictReader(csv_file)
        # Iterate through each line in the CSV file
        for id, item in enumerate(reader):
            # The default ID value is incremented with the row number
            fields["Name"]["default"] = id + 1
            ap_dict = parse_row_data(item, fields)
            ap_dicts.append(ap_dict)

    return ap_dicts


def parse_row_data(item: dict[str, Any], fields: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """
    Parse the data of an Analysis Point row item in a CSV file.
    Takes a 'fields' dictionary which contains data on column renaming, default values and datatypes.
    """
    # Split the id and sample_name value from the Name column
    if "_#" in item["Name"]:
        item["sample_name"], item["Name"] = item["Name"].rsplit("_#", maxsplit=1)

    # If there is a Z column which is requried for the laser, then remove it
    if "Z" in item:
        item.pop("Z")

    ap_dict = {}
    for field, field_data in fields.items():
        # If the field is found and it is not empty, use it
        # Otherwise, use the default value
        if field in item and item[field] != "":
            new_value = item[field]
        else:
            new_value = field_data["default"]

        # Add the field value to the new dictionary
        # using the new header and converting it to the correct type
        ap_dict[field_data["new_header"]] = field_data["type"](new_value)
    return ap_dict


def export_tactool_csv(filepath: str, headers: list[str], analysis_points: list[AnalysisPoint]) -> None:
    """
    Write the given header data and analysis points to the given filepath.
    This is specifically for TACtool Analysis Point data.
    """
    with open(filepath, "w", newline="") as csvfile:
        csvwriter = writer(csvfile)
        # Modify and write the header data
        new_headers = convert_export_headers(headers)
        csvwriter.writerow(new_headers)
        for analysis_point in analysis_points:
            csv_row = convert_export_point(analysis_point, headers)
            csvwriter.writerow(csv_row)


def convert_export_headers(headers: list[str]) -> list[str]:
    """
    Convert the header data for a CSV export.
    This will rename some headers, remove sample_name, and add a Z field.
    """
    header_conversions = {
        "id": "Name",
        "label": "Type",
        "x": "X",
        "y": "Y",
    }
    new_headers = [
        header_conversions[old_header]
        if old_header in header_conversions
        else old_header
        for old_header in headers
    ]
    # Remove the sample_name field, it is concatenated with ID
    new_headers.pop(new_headers.index("sample_name"))

    # Insert a new Z column after the Y column for the laser formatting
    z_index = new_headers.index("Y") + 1
    new_headers.insert(z_index, "Z")
    return new_headers


def convert_export_point(analysis_point: AnalysisPoint, headers: list[str]) -> list:
    """
    Convert an Analysis Point for a CSV export.
    This will concatenate the ID and sample_name into a single field,
    and add a Z field.
    """
    analysis_point_row = analysis_point.aslist()[:len(headers)]

    # Concat the sample_name and id into 1 column
    # Also pads zeros on id column value
    analysis_point_row[headers.index("id")] = f"{analysis_point.sample_name}_#{analysis_point.id:03d}"
    analysis_point_row.pop(headers.index("sample_name"))

    # Insert a new Z column after the Y column for the laser formatting
    analysis_point_row.insert(headers.index("y") + 1, 0)
    return analysis_point_row


def parse_sem_csv(filepath: str, required_headers: list[str]) -> tuple[list[dict[str, Any]], list[str]]:
    """
    Parse an SEM CSV file.
    Returns a list of dictionary rows, and the list of headers in the same order they are in the current file.
    """
    point_dicts = []
    with open(filepath) as csv_file:
        reader = DictReader(csv_file)

        # Check that the given CSV file has the required headers
        reader.fieldnames
        for header in required_headers:
            if header not in reader.fieldnames:
                raise KeyError(f"Missing required header: {header}")

        # Iterate through each line in the CSV file
        for item in reader:
            # Convert the required coordinate headers to floats
            for header in required_headers:
                item[header] = float(item[header])
            point_dicts.append(item)

    return point_dicts, reader.fieldnames


def export_sem_csv(filepath: str, headers: list[str], points: list[dict[str, Any]]) -> None:
    """
    Write the given header data and point data to the given filepath.
    This is specifically for SEM data.
    """
    with open(filepath, "w", newline="") as csvfile:
        csvwriter = writer(csvfile)
        csvwriter.writerow(headers)
        for point in points:
            # Convert the dictionary to a list of values matching the header positions
            csv_row = [point[header] for header in headers]
            csvwriter.writerow(csv_row)


def reset_id(analysis_point: AnalysisPoint) -> AnalysisPoint:
    """
    Reset the ID value of a given Analysis Point.
    """
    analysis_point.id = None
    return analysis_point
