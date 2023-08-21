from textwrap import dedent
from typing import (
    Callable,
    Optional,
)

from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from tactool.analysis_point import (
    AnalysisPoint,
    export_tactool_csv,
    parse_tactool_csv,
    reset_id,
)
from tactool.graphics_view import GraphicsView
from tactool.recoordinate_dialog import RecoordinateDialog
from tactool.set_scale_dialog import SetScaleDialog
from tactool.table_model import TableModel
from tactool.table_view import TableView
from tactool.utils import LoggerMixin


class Window(QMainWindow, LoggerMixin):
    """
    PyQt QMainWindow class which displays the application's interface and
    manages user interaction with it.
    """
    def __init__(self, testing_mode: bool) -> None:
        super().__init__()
        self.testing_mode = testing_mode

        self.default_settings = {
            "metadata": "",
            "label": "RefMark",
            "diameter": 10,
            "scale": "1.0",
            "colour": "#ffff00",
            "csv_format": "*.csv",
            "image_format": "(*.png *.jpg *.jpeg *.tif)",
        }

        # Defining window variables
        self.image_filepath: Optional[str] = None
        self.csv_filepath: Optional[str] = None
        # point_colour is stored as a class vairable because it requires formatting
        # this variable is the formatted version ready to use for other functions
        self.point_colour: str = self.default_settings["colour"]

        # Setup the User Interface
        self.setWindowTitle("TACtool")
        self.setMinimumSize(750, 650)
        self.graphics_view = GraphicsView()
        self.graphics_scene = self.graphics_view.graphics_scene
        self.table_model = TableModel()
        self.table_view = TableView(self.table_model)
        self.set_scale_dialog: Optional[SetScaleDialog] = None
        self.recoordinate_dialog: Optional[RecoordinateDialog] = None
        self.current_message: Optional[QMessageBox] = None
        self.setup_ui_elements()
        self.connect_signals_and_slots()
        self.status_bar_messages = self.create_status_bar_messages()
        self.toggle_status_bar_messages()
        self.main_input_widgets: list[QWidget] = [
            self.menu_bar_file,
            self.sample_name_input,
            self.mount_name_input,
            self.material_input,
            self.label_input,
            self.colour_button,
            self.diameter_input,
            self.set_scale_button,
            self.reset_ids_button,
            self.reset_settings_button,
            self.clear_points_button,
            self.table_view,
        ]


    def setup_ui_elements(self) -> None:
        """
        Setup the User Interface elements.
        """
        self.logger.debug("Setting up UI elements")
        # Create the menu bar
        self.menu_bar = self.menuBar()
        # Create the file drop down
        self.menu_bar_file = self.menu_bar.addMenu("&File")
        # Add buttons to the file drop down
        self.menu_bar_file_import_image = self.menu_bar_file.addAction("Import Image")
        self.menu_bar_file_export_image = self.menu_bar_file.addAction("Export Image")
        self.menu_bar_file.addSeparator()
        self.menu_bar_file_import_tactool_csv = self.menu_bar_file.addAction("Import TACtool CSV")
        self.menu_bar_file_export_tactool_csv = self.menu_bar_file.addAction("Export TACtool CSV")
        self.menu_bar_file.addSeparator()
        self.menu_bar_recoordinate_csv = self.menu_bar_file.addAction("Recoordinate SEM CSV")

        # Create the status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        # Input for metadata
        sample_name_label = QLabel("Sample Name:")
        self.sample_name_input = QLineEdit()
        mount_name_label = QLabel("Mount Name:")
        self.mount_name_input = QLineEdit()
        material_label = QLabel("Material:")
        self.material_input = QLineEdit()

        # Input for Analysis Point label
        point_label_input_label = QLabel("Label:")
        self.label_input = QComboBox()
        self.label_input.addItems(["RefMark", "Spot"])

        # Button for selecting colour
        colour_label = QLabel("Colour:")
        self.colour_button = QPushButton(" " * 20, self)
        self.colour_button.setToolTip("Opens colour dialog")
        self.set_colour_button_style()

        # Input for point diameter
        diameter_label = QLabel("Diameter (μm):")
        self.diameter_input = QSpinBox()
        self.diameter_input.setValue(self.default_settings["diameter"])
        self.diameter_input.setMaximum(100000)

        # Input for scaling
        scale_label = QLabel("Scale (Pixels per µm):")
        self.scale_value_input = QLineEdit()
        self.scale_value_input.setText(self.default_settings["scale"])
        self.scale_value_input.setDisabled(True)
        self.set_scale_button = QPushButton("Set Scale", self)

        # Main buttons
        self.clear_points_button = QPushButton("Clear Points", self)
        self.reset_ids_button = QPushButton("Reset IDs", self)
        self.reset_settings_button = QPushButton("Reset Settings", self)

        # Arrange the layout of the user interface
        sidebar = QVBoxLayout()

        # Metadata input
        sidebar.addWidget(sample_name_label)
        sidebar.addWidget(self.sample_name_input)
        sidebar.addWidget(mount_name_label)
        sidebar.addWidget(self.mount_name_input)
        sidebar.addWidget(material_label)
        sidebar.addWidget(self.material_input)
        sidebar.addStretch(stretch=1)

        # Analysis Point Settings
        sidebar.addWidget(point_label_input_label)
        sidebar.addWidget(self.label_input)
        sidebar.addWidget(colour_label)
        sidebar.addWidget(self.colour_button)
        sidebar.addStretch(stretch=1)

        # Scaling widgets
        sidebar.addWidget(diameter_label)
        sidebar.addWidget(self.diameter_input)
        sidebar.addWidget(scale_label)
        sidebar.addWidget(self.scale_value_input)
        sidebar.addWidget(self.set_scale_button)
        sidebar.addStretch(stretch=6)

        # Main buttons
        sidebar.addWidget(self.reset_ids_button)
        sidebar.addWidget(self.reset_settings_button)
        sidebar.addWidget(self.clear_points_button)

        # Main widgets
        main_view = QVBoxLayout()
        main_view.addWidget(self.graphics_view, stretch=4)
        main_view.addWidget(self.table_view, stretch=1)

        # Set the central widget of the main window
        layout = QHBoxLayout()
        layout.addLayout(sidebar)
        layout.addLayout(main_view, stretch=4)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


    def connect_signals_and_slots(self) -> None:
        """
        Connect signals and slots to User Interface interactions.
        """
        self.logger.debug("Connecting signals and slots")
        # Connect menu bar clicks to handlers
        self.menu_bar_file_import_image.triggered.connect(self.import_image_get_path)
        self.menu_bar_file_export_image.triggered.connect(self.export_image_get_path)
        self.menu_bar_file_import_tactool_csv.triggered.connect(self.import_tactool_csv_get_path)
        self.menu_bar_file_export_tactool_csv.triggered.connect(self.export_tactool_csv_get_path)
        self.menu_bar_recoordinate_csv.triggered.connect(self.toggle_recoordinate_dialog)

        # Connect button clicks to handlers
        self.clear_points_button.clicked.connect(self.clear_analysis_points)
        self.reset_ids_button.clicked.connect(lambda: self.reload_analysis_points(transform=reset_id))
        self.reset_settings_button.clicked.connect(self.reset_settings)
        self.colour_button.clicked.connect(self.get_point_colour)
        self.set_scale_button.clicked.connect(self.toggle_scaling_mode)

        # Connect Graphics View interactions to handlers
        self.graphics_view.left_click.connect(self.add_analysis_point)
        self.graphics_view.right_click.connect(self.remove_analysis_point)

        # Connect Table interaction clicks to handlers
        self.table_view.selected_analysis_point.connect(self.get_point_settings)
        self.table_model.invalid_label_entry.connect(self.show_message)
        self.table_model.updated_analysis_points.connect(self.reload_analysis_points)


    @property
    def dialogs(self) -> list[QDialog]:
        """
        Return a list of the current dialog attributes.
        """
        dialogs = [
            self.set_scale_dialog,
            self.recoordinate_dialog,
        ]
        return dialogs


    def set_colour_button_style(self) -> None:
        """
        Set the CSS stylesheet of the Colour Button in the User Interface.
        """
        colour_button_stylesheet = """
            QToolTip {
                background-color: white;
                color: black;
                border: black solid 1px;
            };
            background-color: #BTN_COLOUR;
            border: none;
        """.replace("#BTN_COLOUR", self.point_colour)
        self.colour_button.setStyleSheet(colour_button_stylesheet)


    def create_status_bar_messages(self) -> dict[str, dict[str, None | QLabel | Callable[[], tuple[bool, str]]]]:
        """
        Create the status bar message functions.
        """
        # Each of these functions contains the condition for the status message and the message itself
        # These must be functions so that the conditional statement is dynamic
        def ref_points(self: Window):
            condition = len(self.table_model.reference_points) < 3
            default_label = self.default_settings["label"]
            message = f"You must have at least 3 points labelled {default_label} as reference points."
            return condition, message

        def set_scale(self: Window):
            condition_1 = self.scale_value_input.text() == self.default_settings["scale"]
            condition_2 = len(self.table_model.reference_points) >= 3
            condition = condition_1 and condition_2
            message = "Have you set a scale?"
            return condition, message

        # Create a dictionary of all status messages
        default_status = None
        status_bar_messages = {
            "ref_points": {
                "status": default_status,
                "function": ref_points,
            },
            "set_scale": {
                "status": default_status,
                "function": set_scale,
            },
        }
        return status_bar_messages


    def toggle_status_bar_messages(self) -> None:
        """
        Toggle all of the status bar messages.
        """
        self.logger.debug("Toggling %s status bar messages", len(self.status_bar_messages))
        for status_name in self.status_bar_messages:
            # Get the status, condition result and message from the dictionary
            status = self.status_bar_messages[status_name]["status"]
            condition, message = self.status_bar_messages[status_name]["function"](self)
            if condition:
                # If the message is not already displayed
                if not status:
                    # Create a PyQt QLabel to display the message in the status bar
                    label = QLabel(message)
                    # Define the font size outside of the CSS stylesheet so that PyQt makes it adaptive
                    label.setFont(QFont("Arial", 16))
                    label.setStyleSheet("""
                        color: red;
                        font-weight: bold;
                        margin: 2;
                        position: absolute;
                    """)
                    self.status_bar.addWidget(label)
                    self.status_bar_messages[status_name]["status"] = label
            # Else if the message is currently displayed
            elif status:
                self.status_bar.removeWidget(status)
                self.status_bar_messages[status_name]["status"] = None


    def import_image_get_path(self) -> None:
        """
        Function to create a PyQt File Dialog, allowing the user to visually select an image file to import.
        """
        pyqt_open_dialog = QFileDialog.getOpenFileName(
            parent=self,
            directory="Import Image",
            filter=self.default_settings["image_format"],
        )
        filepath = pyqt_open_dialog[0]
        if filepath:
            try:
                self.graphics_view.load_image(filepath)
                self.image_filepath = filepath
                self.setWindowTitle(f"TACtool: {self.image_filepath}")
            except Exception as error:
                self.data_error_message(error)


    def export_image_get_path(self) -> None:
        """
        Function to create a PyQt File Dialog, allowing the user to visually select a directory to export an image file.
        """
        if self.validate_current_data(validate_image=True):
            current_filepath = self.image_filepath if self.image_filepath else ""
            pyqt_save_dialog = QFileDialog.getSaveFileName(
                parent=self,
                caption="Export Image",
                directory=current_filepath,
                filter=self.default_settings["image_format"],
            )
            filepath = pyqt_save_dialog[0]
            if filepath:
                try:
                    self.graphics_view.save_image(filepath)
                except Exception as error:
                    self.data_error_message(error)


    def import_tactool_csv_get_path(self) -> None:
        """
        Function to create a PyQt File Dialog, allowing the user to visually select a TACtool CSV file to import.
        """
        pyqt_open_dialog = QFileDialog.getOpenFileName(
            parent=self,
            caption="Import TACtool CSV",
            filter=self.default_settings["csv_format"],
        )
        filepath = pyqt_open_dialog[0]
        if filepath:
            try:
                self.load_tactool_csv_data(filepath)
                self.csv_filepath = filepath
            except Exception as error:
                self.data_error_message(error)


    def load_tactool_csv_data(self, filepath: str) -> None:
        """
        Load the Analysis Point data from a given CSV file and add it into the program.
        """
        try:
            self.logger.info("Loading TACtool CSV file: %s", filepath)
            analysis_points = parse_tactool_csv(filepath, self.default_settings)
            self.clear_analysis_points()
            self.reset_settings()
            # Track if any of the points extend the image boundary
            extends_boundary = False
            image_size = self.graphics_view._image.pixmap().size()
            for analysis_point in analysis_points:
                self.add_analysis_point(**analysis_point, from_click=False)
                ap_x = analysis_point["x"]
                ap_y = analysis_point["y"]
                if ap_x > image_size.width() or ap_x < 0 or ap_y > image_size.height() or ap_y < 0:
                    extends_boundary = True
            self.table_view.scrollToTop()

            # Create a message informing the user that the points extend the image boundary
            if extends_boundary:
                message = "At least 1 of the imported analysis points goes beyond the current image boundary"
                self.logger.warning(message)
                self.show_message(
                    "Imported Points Warning",
                    message,
                    "warning",
                )

        # A KeyError and UnicodeError usually occur with an incorrectly formatted CSV file
        except (KeyError, UnicodeError):
            # Show a message to the user informing them of which headers should be in the CSV file
            required_headers = [
                "    " + val
                for val in ["Name", "Type", "X", "Y", "diameter", "scale", "colour", "mount_name", "material", "notes"]
            ]
            message = "\n".join([
                "There was an error when loading data from CSV file:",
                "   " + filepath.split('/')[-1] + "\n",
                "Plese use a CSV file with the following headers:",
                *required_headers,
            ])
            self.show_message("Error loading data", message, "warning")


    def export_tactool_csv_get_path(self) -> None:
        """
        Function to create a PyQt File Dialog,
        allowing the user to visually select a directory to save a TACtool CSV file.
        """
        if self.validate_current_data():
            current_filepath = self.csv_filepath if self.csv_filepath else ""
            pyqt_save_dialog = QFileDialog.getSaveFileName(
                parent=self,
                caption="Export as TACtool CSV",
                directory=current_filepath,
                filter=self.default_settings["csv_format"],
            )
            filepath = pyqt_save_dialog[0]
            if filepath:
                try:
                    self.logger.info("Exporting Analysis Points to: %s", filepath)
                    export_tactool_csv(
                        filepath=filepath,
                        headers=self.table_model.public_headers,
                        analysis_points=self.table_model.analysis_points,
                    )
                except Exception as error:
                    self.data_error_message(error)


    def validate_current_data(self, validate_image: bool = False) -> bool:
        """
        Check if the current data of the Analysis Points is valid.
        Used when exporting data to a file.
        Each validation step contains a return statement which is used
        when the validation fails, thus preventing the remaining validation.
        """
        # If the validation should also check the image
        if validate_image:
            # If there is currently no image in the PyQt Graphics View
            if self.graphics_view._empty:
                message = dedent("""
                    Image not found.

                    There is no image to save.
                """)
                # This is an information dialog, meaning it can only return True
                if self.show_message("Warning", message, "warning"):
                    return False

        # If there are less than 3 reference points
        if len(self.table_model.reference_points) < 3:
            default_label = self.default_settings["label"]
            message = dedent(f"""
                Missing reference points.

                There must be at least 3 points labelled '{default_label}'.

                Do you still want to continue?
            """)
            # If the user presses Cancel
            if not self.show_message("Warning", message, "question"):
                return False

        # If the scale value has not been changed
        if self.scale_value_input.text() == self.default_settings["scale"]:
            message = dedent("""
                A scale value has not been set.

                Do you still want to continue?
            """)
            # If the user presses Cancel
            if not self.show_message("Warning", message, "question"):
                return False

        # If all checks are passed then continue
        return True


    def add_analysis_point(
        self,
        x: int,
        y: int,
        apid: Optional[int] = None,
        label: Optional[str] = None,
        diameter: Optional[int] = None,
        scale: Optional[float] = None,
        colour: Optional[str] = None,
        sample_name: str = "",
        mount_name: str = "",
        material: str = "",
        notes: str = "",
        from_click: bool = True,
    ) -> None:
        """
        Add an Analysis Point to the PyQt Graphics Scene.
        The main ways a user can do this is by clicking on the Graphics Scene, or by importing a TACtool CSV file.

        If the Analysis Point has been created from a click, get the values from the window settings.
        Otherwise, from_click is set to False and the Analysis Point settings are retrieved from the CSV columns.
        """
        if from_click:
            # Get the required input values from the window input settings
            # Coordinates and the Point ID are taken from the arguments, notes defaults to None
            label = self.label_input.currentText()
            diameter = self.diameter_input.value()
            colour = self.point_colour
            scale = float(self.scale_value_input.text())
            sample_name = self.sample_name_input.text()
            mount_name = self.mount_name_input.text()
            material = self.material_input.text()

        # If no analysis point ID is given, assign it the next ID available
        if not apid:
            apid = self.table_model.next_point_id

        # Get the graphics items for the analysis point
        outer_ellipse, inner_ellipse, label_text_item = self.graphics_scene.add_analysis_point(
            x=x,
            y=y,
            apid=apid,
            label=label,
            diameter=diameter,
            colour=colour,
            scale=scale,
        )

        # Place the new point data into an Analysis Point object
        analysis_point = AnalysisPoint(
            x=x,
            y=y,
            id=apid,
            label=label,
            diameter=diameter,
            scale=scale,
            colour=colour,
            sample_name=sample_name,
            mount_name=mount_name,
            material=material,
            notes=notes,
            _outer_ellipse=outer_ellipse,
            _inner_ellipse=inner_ellipse,
            _label_text_item=label_text_item,
        )
        self.table_model.add_point(analysis_point)
        self.logger.debug("Created Analysis Point: %s", analysis_point)
        self.logger.info("Creating Analysis Point with ID: %s", analysis_point.id)

        # Update the status bar messages and PyQt Table View
        self.toggle_status_bar_messages()
        self.table_view.model().layoutChanged.emit()


    def remove_analysis_point(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        apid: Optional[int] = None,
    ) -> None:
        """
        Remove an Analysis Point from the PyQt Graphics Scene and Table Model.
        The Point is specified using it's coordinates or it's ID value.
        """
        analysis_point = None
        # If a target ID is provided, get the Analysis Point using it's ID
        if apid:
            analysis_point = self.table_model.get_point_by_apid(apid)

        # Else when the user right clicks on the Graphics View to remove an Analysis Point
        elif x and y:
            # Get the ellipse and check it exists
            ellipse = self.graphics_scene.get_ellipse_at(x, y)
            if ellipse:
                # Get the corresponding Analysis Point object of the ellipse
                analysis_point = self.table_model.get_point_by_ellipse(ellipse)

        if analysis_point is not None:
            self.table_model.remove_point(analysis_point.id)
            self.graphics_scene.remove_graphics_items([
                analysis_point._outer_ellipse,
                analysis_point._inner_ellipse,
                analysis_point._label_text_item,
            ])
            # Update the status bar messages and PyQt TableView
            self.toggle_status_bar_messages()
            self.table_view.model().layoutChanged.emit()

            self.logger.info("Deleted Analysis Point: %s", analysis_point.id)


    def reload_analysis_points(
        self,
        index: Optional[QModelIndex] = None,
        transform: Optional[Callable[[AnalysisPoint], AnalysisPoint]] = None,
    ) -> None:
        """
        Function to reload all of the existing Analysis Points.
        Takes an index which indicates if the TableView should be automatically scrolled to a specific point.
        Also takes a transform function to transform the existing Analysis Points before replacing them.
        """
        self.logger.debug("Reloading Analysis Points with transform: %s", transform)
        # Save the existing Points before clearing them
        current_analysis_points = self.table_model.analysis_points
        self.clear_analysis_points()
        # Iterate through each previously existing Point and recreate it
        for analysis_point in current_analysis_points:
            analysis_point = transform(analysis_point)
            self.add_analysis_point(
                x=analysis_point.x,
                y=analysis_point.y,
                apid=analysis_point.id,
                label=analysis_point.label,
                diameter=analysis_point.diameter,
                scale=analysis_point.scale,
                colour=analysis_point.colour,
                sample_name=analysis_point.sample_name,
                mount_name=analysis_point.mount_name,
                material=analysis_point.material,
                notes=analysis_point.notes,
                from_click=False
            )

        # Index is given when the user edits a cell in the PyQt Table View
        # It represents the index of the modified cell
        if index is not None:
            # When the Analysis Points are reloaded, the scroll position in the PyQt Table View resets
            # Therefore, we scroll back to where the user was previously scrolled
            self.table_view.scrollTo(index)


    def clear_analysis_points(self) -> None:
        """
        Clear all existing Analysis Points.
        """
        for point in self.table_model.analysis_points:
            self.remove_analysis_point(apid=point.id)


    def get_point_colour(self) -> None:
        """
        Get a new colour from the user through a QColorDialog.
        """
        # Create a PyQt Colour Dialog to select a colour
        colour = QColorDialog.getColor()
        if colour.isValid():
            # Update the colour of the button and the value
            # colour is a QColor class
            hex_colour = colour.name()
            self.set_point_colour(hex_colour)


    def set_point_colour(self, colour: str) -> None:
        """
        Set the currently selected colour as the given colour.
        Also updates the stylesheet for the GUI colour button to reflect the change.
        """
        self.point_colour = colour
        self.set_colour_button_style()


    def get_point_settings(self, analysis_point: AnalysisPoint, clicked_column_index: int) -> None:
        """
        Get the settings of an Analysis Point which has been selected in the PyQt Table View.
        These settings are then updated to be the current settings.
        """
        self.logger.info("Selected Analysis Point with ID: %s", analysis_point.id)
        # If the column of the cell the user clicked is the id
        if clicked_column_index == self.table_model.headers.index("id"):
            # Update the Analysis Point settings to be the same as the Point settings of the Point selected in the table
            self.update_point_settings(
                label=analysis_point.label,
                diameter=analysis_point.diameter,
                scale=analysis_point.scale,
                colour=analysis_point.colour,
                sample_name=analysis_point.sample_name,
                mount_name=analysis_point.mount_name,
                material=analysis_point.material,
            )


    def reset_settings(self) -> None:
        """
        Reset input fields and general Analysis Point settings to default.
        """
        self.update_point_settings(
            label=self.default_settings["label"],
            diameter=self.default_settings["diameter"],
            scale=self.default_settings["scale"],
            colour=self.default_settings["colour"],
            sample_name=self.default_settings["metadata"],
            mount_name=self.default_settings["metadata"],
            material=self.default_settings["metadata"],
        )


    def update_point_settings(
        self,
        label: Optional[str] = None,
        diameter: Optional[int] = None,
        scale: Optional[str | float] = None,
        colour: Optional[str] = None,
        sample_name: Optional[str] = None,
        mount_name: Optional[str] = None,
        material: Optional[str] = None,
    ) -> None:
        """
        Update the Analysis Point settings to be the given settings.
        If a value is given for a field, then the value and any corresponding
        User Interface elements are updated.
        """
        self.logger.debug(
            (
                "Updating Analysis Point settings: label='%s' diamter='%s', scale='%s', colour='%s', "
                "sample_name='%s', mount_name='%s', material='%s'"
            ),
            label, diameter, scale, colour, sample_name, mount_name, material
        )

        if label is not None:
            self.label_input.setCurrentText(label)

        if diameter is not None:
            self.diameter_input.setValue(diameter)

        if scale is not None:
            self.scale_value_input.setText(str(scale))
            self.toggle_status_bar_messages()

        if colour is not None:
            self.set_point_colour(colour)

        if sample_name is not None:
            self.sample_name_input.setText(sample_name)

        if mount_name is not None:
            self.mount_name_input.setText(mount_name)

        if material is not None:
            self.material_input.setText(material)


    def toggle_main_input_widgets(self, enable: bool) -> None:
        """
        Toggle each of the input widgets in the main window to be enabled or disabled.
        """
        self.logger.debug("Toggling main widgets to state: %s", enable)
        for widget in self.main_input_widgets:
            widget.setEnabled(enable)
        self.graphics_scene.toggle_transparent_window(self.graphics_view._image)
        self.graphics_view.disable_analysis_points = not enable


    def set_scale(self, scale: float) -> None:
        """
        Set the scale of the program given when the Set scale button is clicked in the Set Scale dialog box.
        """
        self.scale_value_input.setText(str(scale))
        self.toggle_status_bar_messages()


    def toggle_scaling_mode(self) -> None:
        """
        Function to toggle the program's scaling mode functionality.
        """
        # Toggle the scaling mode for the Graphics View
        self.graphics_view.toggle_scaling_mode()

        # If the program is not in scaling mode
        if self.set_scale_dialog is None:
            self.set_scale_dialog = SetScaleDialog(self.testing_mode)
            self.toggle_main_input_widgets(False)
            # Move the Dialog box to be at the top left corner of the main window
            main_window_pos = self.pos()
            self.set_scale_dialog.move(main_window_pos.x() + 50, main_window_pos.y() + 50)

            # Connect the Set Scale dialog buttons
            self.set_scale_dialog.set_scale_clicked.connect(self.set_scale)
            self.set_scale_dialog.clear_scale_clicked.connect(self.graphics_view.reset_scaling_elements)
            self.set_scale_dialog.closed_set_scale_dialog.connect(self.toggle_scaling_mode)
            self.graphics_view.scale_move_event.connect(self.set_scale_dialog.scale_move_event_handler)

        # Else when the program is in scaling mode, reset the Set Scaling Dialog value
        else:
            self.set_scale_dialog = None
            # Enable main window widgets
            self.toggle_main_input_widgets(True)


    def toggle_recoordinate_dialog(self) -> None:
        """
        Toggle the recoordination dialog window.
        """
        # If there are 3 reference points which can be used for recoordination
        if len(self.table_model.reference_points) >= 3:
            # If the program is not in recoordination mode
            if self.recoordinate_dialog is None:
                # Create the Recoordinate Dialog box
                self.recoordinate_dialog = RecoordinateDialog(
                    testing_mode=self.testing_mode,
                    ref_points=self.table_model.reference_points,
                    image_size=self.graphics_view._image.pixmap().size(),
                )
                # Disable main window input widgets
                self.toggle_main_input_widgets(False)
                # Move the Dialog box to be at the top left corner of the main window
                main_window_pos = self.pos()
                self.recoordinate_dialog.move(main_window_pos.x() + 50, main_window_pos.y() + 50)

                # Connect the Recoordinate dialog buttons
                self.recoordinate_dialog.closed_recoordinate_dialog.connect(self.toggle_recoordinate_dialog)
                self.recoordinate_dialog.show_message.connect(self.show_message)

            # Else when the program is in recoordination mode, reset the Recoordination Dialog value
            else:
                self.recoordinate_dialog = None
                # Enable main window widgets
                self.toggle_main_input_widgets(True)
        else:
            self.logger.error("Missing 3 references points for recoordination")
            self.show_message(
                "Reference Points",
                "3 Reference points are required to perform recoordination.",
                "warning",
            )


    def data_error_message(self, error: Exception) -> None:
        """
        Show an error message to the user in the event that
        an error occurs when loading in data.
        """
        self.show_message(
            "Error loading data",
            f"An unexpected error occured: {error}",
            "warning",
        )


    def show_message(self, title: str, message: str, type: str) -> bool:
        """
        Show a given message to the user in a PyQt QMessageBox.
        """
        # In testing mode, the user cannot select an option for the message dialog
        if not self.testing_mode:
            # Creating the PyQt Message box and formatting it
            self.current_message = QMessageBox()
            self.current_message.setWindowTitle(title)
            self.current_message.setText(message)
            self.current_message.setStandardButtons(QMessageBox.Ok)

            # Set the type of message
            type_dict = {
                "warning": QMessageBox.Warning,
                "information": QMessageBox.Information,
                "question": QMessageBox.Question,
            }
            self.current_message.setIcon(type_dict[type])
            if type == "question":
                self.current_message.setIcon(QMessageBox.Question)
                self.current_message.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)

            # Show the message box
            message_box = self.current_message.exec_()

            self.current_message = None
            # If the user presses the Cancel button on the message box
            if message_box == QMessageBox.Cancel:
                return False
        return True


    def closeEvent(self, event=None) -> None:
        """
        Function which is run by PyQt when the application is closed.
        """
        # Close any open dialogs
        for dialog in self.dialogs:
            if dialog is not None:
                dialog.close()
