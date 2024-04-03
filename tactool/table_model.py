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
    QMessageBox,
)

from tactool.analysis_point import AnalysisPoint
from tactool.utils import LoggerMixin


class TableModel(QAbstractTableModel, LoggerMixin):
    """
    PyQt QAbstractTableModel for storing AnalysisPoints.
    """
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
        Set and return the header values from the QAbstractTableModel.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headers[section]
            else:
                return str(section)


    def columnCount(self, *args) -> int:
        """
        Return the number of columns in the QAbstractTableModel.
        Internal method for PyQt.
        """
        return len(self.headers)


    def rowCount(self, *args) -> int:
        """
        Return the number of rows in the QAbstractTableModel.
        Internal method for PyQt.
        """
        return len(self._data)


    def data(self, index: QModelIndex, role: int) -> Optional[str]:
        """
        Format the data to be displayed in the QAbstractTableModel.
        It is called when displaying values in the cells, also called when editing (doubleclick).
        Internal method for PyQt.
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
        Update the value in a cell of the QAbstractTableModel.
        It is called when editing a value in an editable cell.
        Internal method for PyQt.
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
                    QMessageBox.warning(
                        None,
                        "Invalid Label",
                        f"'{value}' is not a valid label.\n\nPlease use either 'Spot' or 'RefMark'.",
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
        Set the flags of the cells within the QAbstractTableModel.
        Internal method for PyQt.
        """
        # Set all columns to be selectable and enabled
        default_flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        # If the given column should be an editable column, set it to be editable
        if index.column() in self.editable_columns:
            return default_flags | Qt.ItemIsEditable
        else:
            return default_flags


    def add_point(self, analysis_point: AnalysisPoint) -> None:
        """
        Add an Analysis Point object as a row.
        """
        self._data.append(analysis_point.aslist())


    def remove_point(self, target_id: int) -> None:
        """
        Remove an Analysis Point object using it's ID value.
        """
        for index, analysis_point in enumerate(self.analysis_points):
            if target_id == analysis_point.id:
                self._data.pop(index)
                break


    def get_point_by_ellipse(self, target_ellipse: QGraphicsEllipseItem) -> AnalysisPoint:
        """
        Get the data of an Analysis Point object using its ellipse object.
        """
        for analysis_point in self.analysis_points:
            if target_ellipse in [analysis_point._outer_ellipse, analysis_point._inner_ellipse]:
                return analysis_point


    def get_point_by_apid(self, target_id: int) -> AnalysisPoint:
        """
        Get an Analysis Point using its ID value.
        """
        for analysis_point in self.analysis_points:
            if int(target_id) == analysis_point.id:
                return analysis_point


    @property
    def public_headers(self) -> list[str]:
        """
        Return just the public headers.
        """
        return [header for header in self.headers if not header.startswith("_")]


    @property
    def analysis_points(self) -> list[AnalysisPoint]:
        """
        Return all of the Analysis Points.
        """
        return [AnalysisPoint(*item) for item in self._data]


    @property
    def reference_points(self) -> list[AnalysisPoint]:
        """
        Return Analysis Points which are RefMarks point.
        """
        label_index = AnalysisPoint.field_names().index("label")
        return [AnalysisPoint(*item) for item in self._data if item[label_index] == "RefMark"]


    @property
    def next_point_id(self) -> int:
        """
        Return the current maximum Analysis Point ID value + 1.
        """
        ids = [
            analysis_point.id
            for analysis_point in self.analysis_points
        ]
        if len(ids) == 0:
            return 1
        else:
            return max(ids) + 1
