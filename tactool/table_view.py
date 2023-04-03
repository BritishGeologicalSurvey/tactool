"""
The Table View manages how the data which is stored in the Table Model is displayed in the User Interface.
"""

from PyQt5.QtCore import (
    pyqtSignal,
    Qt,
)
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QTableView

from tactool.table_model import (
    AnalysisPoint,
    TableModel,
)


class TableView(QTableView):
    """
    PyQt QTableView class to display the data of the analysis points from the PyQt QAbstractTableModel.
    """
    # Tracks when a cell in the Table View is selected
    selected_analysis_point = pyqtSignal(AnalysisPoint, int)

    def __init__(self, table_model: TableModel) -> None:
        super().__init__()
        # Setup the Table View with the Table Model and adjust it's settings
        self.setModel(table_model)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.set_column_sizes()


    def set_column_sizes(self) -> None:
        """
        Function to set the sizing of specific columns in the Table View.
        """
        headers = TableModel().headers
        resize_columns = ["id", "x", "y", "label", "diameter", "scale", "colour"]
        # Resize the first 7 columns to be smaller
        for column_name in resize_columns:
            self.setColumnWidth(headers.index(column_name), 100)


    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Function to handle mouse clicks on the Table View.

        Since we are only adding functionality to mousePressEvent, we pass the event to the
        parent PyQt class, QTableView, at the end of the function to handle
        all other event occurences.
        """
        # If the user left clicks on the Table View and there are existing analysis points
        if event.buttons() == Qt.LeftButton and self.model().analysis_points:
            # Get the index of the cell in the table which they clicked on
            index = self.indexAt(event.pos())
            analysis_point = self.model().analysis_points[index.row()]
            self.selected_analysis_point.emit(analysis_point, index.column())
        super().mousePressEvent(event)
