import numpy as np

from PyQt5.QtCore import (
    pyqtSignal,
    Qt,
    QSize,
)
from PyQt5.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from tactool.analysis_point import (
    SEM_HEADERS,
    AnalysisPoint,
    parse_sem_csv,
)
from tactool.utils import LoggerMixin


class RecoordinateDialog(QDialog, LoggerMixin):
    """
    PyQt QDialog class for creating the recoordination dialog box.
    """
    # Tracks when the Recoordinate Dialog Box is closed
    closed_recoordinate_dialog = pyqtSignal()

    def __init__(
        self,
        testing_mode: bool,
        ref_points: list[AnalysisPoint],
        image_size: QSize,
    ) -> None:
        super().__init__()
        self.testing_mode = testing_mode
        self.ref_points = ref_points
        self.image_size = image_size

        # Setting the Dialog Box settings
        self.setWindowTitle("Recoordination")
        self.setMinimumSize(300, 150)
        self.setWindowFlags(
            Qt.Window | Qt.WindowCloseButtonHint
        )
        self.setup_ui_elements()
        self.connect_signals_and_slots()

        # This is used later to save recoordinated points
        self.recoordinated_point_dicts: list[dict[str, str | int | float]] = []

        if not self.testing_mode:
            self.show()


    def setup_ui_elements(self) -> None:
        """
        Create the elements of the Set Scale dialog box User Interface.
        Also sets the layout for the dialog box.
        """
        self.logger.debug("Setting up UI elements")
        # Create the UI elements
        input_csv_label = QLabel("Input CSV")
        self.input_csv_button = QPushButton("Select Input CSV", self)
        self.input_csv_filepath_label = QLineEdit("")
        self.input_csv_filepath_label.setDisabled(True)

        self.recoordinate_button = QPushButton("Import and Recoordinate")
        self.cancel_button = QPushButton("Cancel", self)

        # Arrange the main layout
        layout = QVBoxLayout()
        layout.addWidget(input_csv_label)
        layout.addWidget(self.input_csv_button)
        layout.addWidget(self.input_csv_filepath_label)

        # Add the final 2 buttons alongside eachother
        bottom_button_layout = QHBoxLayout()
        bottom_button_layout.addWidget(self.recoordinate_button)
        bottom_button_layout.addWidget(self.cancel_button)
        layout.addLayout(bottom_button_layout)

        # Set the layout
        self.setLayout(layout)


    def connect_signals_and_slots(self) -> None:
        """
        Function for connecting signals and slots of buttons and input boxes.
        """
        self.logger.debug("Connecting signals and slots")
        self.input_csv_button.clicked.connect(self.get_input_csv)
        self.recoordinate_button.clicked.connect(self.import_and_recoordinate_sem_csv)
        self.cancel_button.clicked.connect(self.closeEvent)


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


    def import_and_recoordinate_sem_csv(self) -> None:
        """
        Get the given CSV file, if it is valid then perform the recoordination process.
        """
        # Check the given paths
        input_csv = self.input_csv_filepath_label.text()
        if input_csv == "":
            QMessageBox.warning(None, "Invalid Path", "Please select an input SEM CSV first.")
            return

        # Get the points from the SEM CSV
        try:
            self.logger.info("Loading SEM CSV: %s", input_csv)
            point_dicts = parse_sem_csv(filepath=input_csv)
        except KeyError as error:
            self.logger.error(error)
            string_headers = "\n".join(SEM_HEADERS.values())
            QMessageBox.warning(
                None,
                "Invalid CSV File",
                f"The given file does not contain the required headers:\n\n{string_headers}",
            )
            return

        # Invert all of the X coordinates because the SEM has an origin at the top right
        # but TACtool has an origin at the top left
        for idx, point_dict in enumerate(point_dicts):
            point_dict["x"] = self.image_size.width() - point_dict["x"]
            point_dicts[idx] = point_dict

        self.recoordinated_point_dicts = self.recoordinate_sem_points(point_dicts)
        self.closeEvent()


    def recoordinate_sem_points(
        self,
        point_dicts: list[dict[str, str | int | float]],
    ) -> list[dict[str, str | int | float]]:
        """
        Recoordinate the given input SEM CSV file points using the current Analysis Points as reference points.
        """
        # Calculate the matrix
        self.logger.debug("Calculating recoordination matrix")
        # For source and dest points, we only use the first 3 reference points
        # Format the points into lists of tuples of x and y values
        source = [
            (item["x"], item["y"])
            for item in point_dicts
            if item["label"] == "RefMark"
        ][:3]
        dest = [
            (point.x, point.y)
            for point in self.ref_points
        ][:3]
        matrix = affine_transform_matrix(source=source, dest=dest)

        # Apply the matrix
        # Track if any of the new points extend the image boundary
        extends_boundary = False
        for idx, item in enumerate(point_dicts):
            point = (item["x"], item["y"])
            new_x, new_y = affine_transform_point(matrix=matrix, point=point)
            point_dicts[idx]["x"] = new_x
            point_dicts[idx]["y"] = new_y
            # Check if the new point extends the image boundary
            if new_x > self.image_size.width() or new_x < 0 or new_y > self.image_size.height() or new_y < 0:
                extends_boundary = True

            self.logger.debug("Transformed point %s to %s", point, (new_x, new_y))
        self.logger.info("Transformed %s points", len(point_dicts))

        # Create a message informing the user that the recoordinated points extend the image boundary
        if extends_boundary:
            message = "At least 1 of the recoordinated points goes beyond the current image boundary"
            self.logger.warning(message)
            QMessageBox.warning(None, "Recoordination Warning", message)

        return point_dicts


    def closeEvent(self, event=None) -> None:
        """
        Function which is run by PyQt when the application is closed.
        """
        self.closed_recoordinate_dialog.emit()


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
    dest = (round(dest[0]), round(dest[1]))  # to 2D integer coordinate

    return dest
