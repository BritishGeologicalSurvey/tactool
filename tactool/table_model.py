"""
The Analysis Point class stores Analysis Point data.

The Table Model acts as a central storage for Analysis Points
and Graphics Scene items.
"""

import dataclasses
from csv import writer
from pathlib import Path
from textwrap import dedent
from typing import (
    Any,
    Optional,
)

from PyQt5.QtCore import (
    pyqtSignal,
    QAbstractTableModel,
    QModelIndex,
    Qt,
)
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
        Function to get the field names of the class object.
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
        Function to get the attributes of an Analysis Point object as a list.
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


class TableModel(QAbstractTableModel):
    """
    PyQt QAbstractTableModel for storing AnalysisPoints.
    """
    # Tracks if a new edited input in the PyQt Table Model is invalid
    invalid_label_entry = pyqtSignal(str, str, str)
    # Tracks if a new edited input in the PyQt Table Model is accepted
    updated_analysis_points = pyqtSignal(QModelIndex)


    def __init__(self) -> None:
        super().__init__()
        # Set the headers of the table to be the names of the Analysis Point attributes
        self.headers = AnalysisPoint.field_names()
        self._data: list[list[Any]] = []
        self.editable_columns = [
            self.headers.index("label"),
            self.headers.index("sample_name"),
            self.headers.index("mount_name"),
            self.headers.index("material"),
            self.headers.index("notes"),
        ]


    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> str:
        """
        Function to set and return the header values from the QAbstractTableModel.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headers[section]
            else:
                return str(section)


    def columnCount(self, *args) -> int:
        """
        Function to return the number of columns in the QAbstractTableModel.
        """
        return len(self.headers)


    def rowCount(self, *args) -> int:
        """
        Function to return the number of rows in the QAbstractTableModel.
        """
        return len(self._data)


    def data(self, index: QModelIndex, role: int) -> Optional[str]:
        """
        Function to format the data to be displayed in the QAbstractTableModel.
        It is called when displaying values in the cells, also called when editing (doubleclick).
        """

        if role == Qt.DisplayRole or role == Qt.EditRole:
            row = index.row()
            col = index.column()
            # Try except solves an unexpected error when editing values in the Table
            try:
                return str(self._data[row][col])
            except IndexError:
                return


    def setData(self, index: QModelIndex, value: str, role: Qt.ItemDataRole = Qt.EditRole) -> bool:
        """
        Function to update the value in a cell of the QAbstractTableModel.
        It is called when editing a value in an editable cell.
        """
        if index.isValid():
            row = index.row()
            column = index.column()

            if column == self.headers.index("label"):
                # Format the new label to aid user with capitalisation
                value = value.upper()
                if value == "SPOT":
                    value = "Spot"
                elif value == "REFMARK":
                    value = "RefMark"
                # If the new label is not one of the required label values
                else:
                    # Create a message informing the user that their input value is invalid
                    message = dedent(f"""
                        '{value}' is not a valid label.

                        Please use either 'Spot' or 'RefMark'.
                    """)
                    self.invalid_label_entry.emit(
                        "Invalid Label",
                        message,
                        "warning",
                    )
                    return False

            # Update the new value
            self._data[row][column] = value
            self.updated_analysis_points.emit(index)
            # Manadtory emit required by PyQt when using setData with a QAbstractTableModel
            self.dataChanged.emit(index, index)
            return True
        return False


    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """
        Function to set the flags of the cells within the QAbstractTableModel.
        """
        # If the given column should be an editable column, set it to be editable
        # Set all columns to be selectable and enabled
        if index.column() in self.editable_columns:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled


    def add_point(self, analysis_point: AnalysisPoint) -> None:
        """
        Function to add an Analysis Point object as a row.
        """
        self._data.append(analysis_point.aslist())


    def remove_point(self, target_id: int) -> None:
        """
        Function to remove an Analysis Point object using it's ID value.
        """
        for index, analysis_point in enumerate(self.analysis_points):
            # If the target ID is equal to the current ID, remove it from the table
            if target_id == analysis_point.id:
                self._data.pop(index)


    def get_point_by_ellipse(self, target_ellipse: QGraphicsEllipseItem) -> AnalysisPoint:
        """
        Function to get the data of an Analysis Point object.
        """
        for analysis_point in self.analysis_points:
            # If the target ellipse is equal to either the current outer or inner ellipse
            if target_ellipse in [analysis_point._outer_ellipse, analysis_point._inner_ellipse]:
                return analysis_point


    def get_point_by_apid(self, target_id: int) -> AnalysisPoint:
        """
        Function to get an Analysis Point using its ID value.
        """
        for analysis_point in self.analysis_points:
            if int(target_id) == analysis_point.id:
                return analysis_point


    @property
    def reference_points(self) -> list[AnalysisPoint]:
        """
        Function to return Analysis Points which are a RefMark point.
        """
        # Using list comprehension to get Analysis Points if their label attribute is equal to RefMark
        label_index = AnalysisPoint.field_names().index("label")
        return [AnalysisPoint(*item) for item in self._data if item[label_index] == "RefMark"]


    @property
    def analysis_points(self) -> list[AnalysisPoint]:
        """
        Function to return all of the Analysis Points.
        """
        # Using list comprehension to get all Analysis Points and unpack their values into Analysis Point objects
        return [AnalysisPoint(*item) for item in self._data]


    def export_csv(self, filepath: Path) -> None:
        """
        Get all the existing Analysis Points and write them to as a CSV file.
        """
        # Do not save the last 3 columns as they contain PyQt graphics data
        with open(filepath, "w", newline="") as csvfile:
            csvwriter = writer(csvfile)
            # Modify and write the header data
            new_headers = self.convert_export_headers()
            csvwriter.writerow(new_headers)
            # Iterate through each existing analysis point and write it's data
            for analysis_point in self.analysis_points:
                csv_row = self.convert_export_point(analysis_point)
                csvwriter.writerow(csv_row)


    def convert_export_headers(self) -> list[str]:
        """
        Function to convert the header data formatting for a CSV export.
        """
        header_conversions = {
            "id": "Name",
            "label": "Type",
            "x": "X",
            "y": "Y",
        }
        headers = self.headers[:len(self.headers) - 3]
        for old_header, new_header in zip(header_conversions, header_conversions.values()):
            headers[headers.index(old_header)] = new_header
        # Remove the sample_name field
        headers.pop(headers.index("sample_name"))

        # Insert a new Z column after the Y column for the laser formatting
        z_index = headers.index("Y") + 1
        headers.insert(z_index, "Z")
        return headers


    def convert_export_point(self, analysis_point: AnalysisPoint) -> list:
        """
        Function to convert an Analysis Point formatting for a CSV export.
        """
        headers = self.headers[:len(self.headers) - 3]
        id_idx, sample_name_idx = headers.index("id"), headers.index("sample_name")
        analysis_point_row = analysis_point.aslist()[:len(self.headers) - 3]

        # Concat the sample_name and id into 1 column
        # Also pads zeros on id column value
        analysis_point_row[id_idx] = f"{analysis_point.sample_name}_#{analysis_point.id:03d}"
        analysis_point_row.pop(sample_name_idx)

        # Insert a new Z column after the Y column for the laser formatting
        z_index = headers.index("y") + 1
        analysis_point_row.insert(z_index, 0)
        return analysis_point_row
