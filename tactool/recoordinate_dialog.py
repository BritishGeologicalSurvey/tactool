"""
The Recoordinate Dialog is used for allowing the user to provide a CSV to be recoordinated.
"""

from PyQt5.QtCore import (
    pyqtSignal,
    Qt,
)
from PyQt5.QtWidgets import (
    QDialog,
    QFileDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from tactool.analysis_point import (
    AnalysisPoint,
    affine_transform_matrix,
    affine_transform_point,
    parse_sem_csv,
    export_sem_csv,
)
from tactool.utils import LoggerMixin


class RecoordinateDialog(QDialog, LoggerMixin):
    """
    PyQt QDialog class for creating the recoordination dialog box.
    """
    # Tracks when the Recoordinate Dialog Box is closed
    closed_recoordinate_dialog = pyqtSignal()
    # Used for showing messages with methods from the main window
    show_message = pyqtSignal(str, str, str)

    def __init__(self, testing_mode: bool, ref_points: list[AnalysisPoint]) -> None:
        super().__init__()
        self.testing_mode = testing_mode
        self.ref_points = ref_points

        # Setting the Dialog Box settings
        self.setWindowTitle("Recoordination")
        self.setMinimumSize(300, 200)
        self.setWindowFlags(
            Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint
        )
        self.setup_ui_elements()
        self.connect_signals_and_slots()

        if not self.testing_mode:
            self.show()


    def setup_ui_elements(self) -> None:
        """
        Function to create the elements of the Set Scale dialog box User Interface.
        Also sets the layout for the dialog box.
        """
        self.logger.debug("Setting up UI elements")
        # Create the UI elements
        input_csv_label = QLabel("Input CSV")
        self.input_csv_button = QPushButton("Select Input CSV", self)
        self.input_csv_filepath_label = QLineEdit("")
        self.input_csv_filepath_label.setDisabled(True)
        output_csv_label = QLabel("Output CSV")
        self.output_csv_button = QPushButton("Select Output CSV", self)
        self.output_csv_filepath_label = QLineEdit("")
        self.output_csv_filepath_label.setDisabled(True)
        self.recoordinate_button = QPushButton("Recoordinate and Export CSV")

        # Arrange and set the layout
        layout = QVBoxLayout()
        layout.addWidget(input_csv_label)
        layout.addWidget(self.input_csv_button)
        layout.addWidget(self.input_csv_filepath_label)
        layout.addWidget(output_csv_label)
        layout.addWidget(self.output_csv_button)
        layout.addWidget(self.output_csv_filepath_label)
        layout.addWidget(self.recoordinate_button)
        self.setLayout(layout)


    def connect_signals_and_slots(self) -> None:
        """
        Function for connecting signals and slots of buttons and input boxes.
        """
        self.logger.debug("Connecting signals and slots")
        self.input_csv_button.clicked.connect(self.get_input_csv)
        self.output_csv_button.clicked.connect(self.set_output_csv)
        self.recoordinate_button.clicked.connect(self.get_export_and_recoordinate)


    def get_input_csv(self) -> None:
        """
        Get the input CSV file for recoordination from the user.
        """
        pyqt_open_dialog = QFileDialog.getOpenFileName(
            self,
            "Import Recoordination CSV",
            filter="*.csv",
        )
        input_csv = pyqt_open_dialog[0]
        self.input_csv_filepath_label.setText(input_csv)
        self.logger.info("Selected input CSV: %s", input_csv)


    def set_output_csv(self) -> None:
        """
        Set the output CSV file for the recoordination results.
        """
        pyqt_save_dialog = QFileDialog.getSaveFileName(
            parent=self,
            caption="Export Recoordinated CSV",
            directory=self.input_csv_filepath_label.text(),
            filter="*.csv",
        )
        output_csv = pyqt_save_dialog[0]
        self.output_csv_filepath_label.setText(output_csv)
        self.logger.info("Selected output CSV: %s", output_csv)


    def get_export_and_recoordinate(self) -> None:
        """
        Get the export CSV file and emit the recoordinate signal back to the main class.
        """
        input_csv = self.input_csv_filepath_label.text()
        output_csv = self.output_csv_filepath_label.text()
        if input_csv != "" and output_csv != "":
            result = self.recoordinate_sem_points(input_csv, output_csv)
            if result:
                self.closeEvent()
        else:
            # Create a message informing the user that their input value is invalid
            self.show_message.emit(
                "Invalid Paths",
                "Please select an input and output CSV first.",
                "warning",
            )


    def recoordinate_sem_points(
        self,
        input_csv: str,
        output_csv: str,
        x_header: str = "Laser Ablation Centre X",
        y_header: str = "Laser Ablation Centre Y",
        ref_col: str = "Mineral Classification",
        ref_label: str = "Fiducial",
    ) -> bool:
        """
        Recoordinate the given input SEM CSV file points using the current Analysis Points as reference points.
        Saves the resulting SEM data to the given output CSV file.
        Returns a bool which signals if the recoordination successfully completed.

        The x_header, y_header, ref_col and ref_label values can be changed to allow recoordination
        of CSV files with different headers and data.
        For example, using the following values would allow recoordination for TACtool CSV files:
        x_header="X", y_header="Y", ref_col="Type", ref_label="RefMark"
        """
        # Parse the SEM CSV data
        required_sem_headers = [x_header, y_header]
        try:
            self.logger.info("Loading SEM CSV: %s", input_csv)
            point_dicts, csv_headers = parse_sem_csv(filepath=input_csv, required_headers=required_sem_headers)
        except KeyError as error:
            self.logger.error(error)
            self.show_message.emit(
                "Invalid CSV File",
                "\n".join(["The given file does not contain the required headers:"] + [
                    "    " + header for header in required_sem_headers
                ]),
                "warning",
            )
            return False

        # Calculate the matrix
        self.logger.debug("Calculating recoordination matrix")
        # Format the source and dest points into lists of tuples of x and y values
        source = [
            (item[x_header], item[y_header])
            for item in point_dicts
            if item[ref_col] == ref_label
        ]
        dest = [(point.x, point.y) for point in self.ref_points]
        matrix = affine_transform_matrix(source=source, dest=dest)

        # Apply the matrix
        for idx, item in enumerate(point_dicts):
            point = (item[x_header], item[y_header])
            new_point = affine_transform_point(matrix=matrix, point=point)
            point_dicts[idx][x_header], point_dicts[idx][y_header] = new_point
            self.logger.debug("Transformed point %s to %s", point, new_point)
        self.logger.info("Transformed %s points", len(point_dicts))

        # Export the new points to the output CSV
        self.logger.info("Saving recoordination results to: %s", output_csv)
        export_sem_csv(filepath=output_csv, headers=csv_headers, points=point_dicts)
        return True


    def closeEvent(self, event=None) -> None:
        """
        Function which is run by PyQt when the application is closed.
        """
        self.closed_recoordinate_dialog.emit()
