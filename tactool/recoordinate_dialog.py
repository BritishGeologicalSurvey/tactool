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


class RecoordinateDialog(QDialog):
    """
    PyQt QDialog class for creating the recoordination dialog box.
    """
    # Tracks when the recoordinate button is clicked
    recoordinate_clicked = pyqtSignal(str, str)
    # Tracks when the Recoordinate Dialog Box is closed
    closed_recoordinate_dialog = pyqtSignal()
    # Tracks when invalid input is supplied
    invalid_path_entry = pyqtSignal(str, str, str)

    def __init__(self, testing_mode: bool) -> None:
        super().__init__()
        self.testing_mode = testing_mode

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
        # Create the UI elements
        input_csv_label = QLabel("Select Input CSV")
        self.input_csv_button = QPushButton("Import CSV", self)
        self.input_csv_filepath_label = QLineEdit("")
        self.input_csv_filepath_label.setDisabled(True)
        output_csv_label = QLabel("Select Output CSV")
        self.recoordinate_button = QPushButton("Recoordinate and Export CSV")

        # Arrange and set the layout
        layout = QVBoxLayout()
        layout.addWidget(input_csv_label)
        layout.addWidget(self.input_csv_button)
        layout.addWidget(self.input_csv_filepath_label)
        layout.addWidget(output_csv_label)
        layout.addWidget(self.recoordinate_button)
        self.setLayout(layout)


    def connect_signals_and_slots(self) -> None:
        """
        Function for connecting signals and slots of buttons and input boxes.
        """
        self.input_csv_button.clicked.connect(self.get_input_csv)
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


    def get_export_and_recoordinate(self) -> None:
        """
        Get the export CSV file and emit the recoordinate signal back to the main class.
        """
        input_csv = self.input_csv_filepath_label.text()
        if input_csv != "":
            pyqt_save_dialog = QFileDialog.getSaveFileName(
                parent=self,
                caption="Export Recoordinated CSV",
                directory=input_csv,
                filter="*.csv",
            )
            output_csv = pyqt_save_dialog[0]
            if output_csv != "":
                self.recoordinate_clicked.emit(input_csv, output_csv)
                self.closeEvent()
        else:
            # Create a message informing the user that their input value is invalid
            self.invalid_path_entry.emit(
                "Invalid Path",
                "Please import a CSV to recoordinate first.",
                "warning",
            )


    def closeEvent(self, event=None) -> None:
        """
        Function which is run by PyQt when the application is closed.
        """
        self.closed_recoordinate_dialog.emit()
