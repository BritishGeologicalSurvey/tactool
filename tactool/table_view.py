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
        self.format_columns()


    def format_columns(self) -> None:
        """
        Format the columns in the TableView.
        This includes sizing specific columns and hiding private fields.
        """
        headers: list[str] = self.model().headers

        # Resize the first 7 columns to be smaller
        resize_columns = ["id", "x", "y", "label", "diameter", "scale", "colour"]
        for column_name in resize_columns:
            self.setColumnWidth(headers.index(column_name), 100)

        # Hide private fields
        for idx, column in enumerate(headers):
            # Columns beginning with an _ store the PyQt Graphics elements corresponding to the Analysis Points
            if column.startswith("_"):
                self.hideColumn(idx)


    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handler for mouse clicks on the Table View.

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
