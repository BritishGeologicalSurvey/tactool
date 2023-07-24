"""
The Window manages the user interface layout and interaction with
buttons and input boxes.
"""

import logging
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

from tactool.graphics_view import GraphicsView
from tactool.recoordinate_dialog import RecoordinateDialog
from tactool.set_scale_dialog import SetScaleDialog
from tactool.table_model import AnalysisPoint
from tactool.table_view import TableView
from tactool.transformation import (
    parse_tactool_csv,
    reset_id,
)

logger = logging.getLogger("tactool")
logger.setLevel(logging.DEBUG)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(message)s",
)


class Window(QMainWindow):
    """
    PyQt QMainWindow class which displays the application's interface and
    manages user interaction with it.
    """
    def __init__(self, testing_mode: bool) -> None:
        super().__init__()
        logger.info("Initialising TACtool application")
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
        self.status_bar_messages = self.create_status_bar_messages()

        # Setup the User Interface
        self.setWindowTitle("TACtool")
        self.setMinimumSize(750, 650)
        self.graphics_view = GraphicsView()
        self.graphics_scene = self.graphics_view.graphics_scene
        self.table_model = self.graphics_view.graphics_scene.table_model
        self.table_view = TableView(self.table_model)
        self.set_scale_dialog: Optional[SetScaleDialog] = None
        self.recoordinate_dialog: Optional[RecoordinateDialog] = None
        self.setup_ui_elements()
        self.connect_signals_and_slots()
        self.toggle_status_bar_messages()
        self.main_input_widgets = [
            self.menu_bar_file,
            self.sample_name_input,
            self.mount_name_input,
            self.material_input,
            self.label_input,
            self.colour_button,
            self.diameter_input,
            self.reset_ids_button,
            self.reset_settings_button,
            self.clear_points_button,
            self.table_view,
        ]


    def setup_ui_elements(self) -> None:
        """
        Function to setup the User Interface elements.
        """
        # Create the menu bar
        self.menu_bar = self.menuBar()
        # Create the file drop down
        self.menu_bar_file = self.menu_bar.addMenu("&File")
        # Add buttons to the file drop down
        self.menu_bar_file_import_image = self.menu_bar_file.addAction("Import Image")
        self.menu_bar_file_export_image = self.menu_bar_file.addAction("Export Image")
        self.menu_bar_file.addSeparator()
        self.file_menu_bar_import_tactool_csv = self.menu_bar_file.addAction("Import TACtool CSV")
        self.file_menu_bar_export_tactool_csv = self.menu_bar_file.addAction("Export TACtool CSV")
        self.menu_bar_file.addSeparator()
        self.menu_bar_recoordinate_csv = self.menu_bar_file.addAction("Recoordinate <TACtool> CSV")

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


    def set_colour_button_style(self) -> None:
        """
        Function to set the CSS stylesheet of the Colour Button in the User Interface.
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


    def connect_signals_and_slots(self) -> None:
        """
        Function for connecting signals and slots of User Interface interactions.
        """
        # Connect menu bar clicks to handlers
        self.menu_bar_file_import_image.triggered.connect(self.import_image_get_path)
        self.menu_bar_file_export_image.triggered.connect(self.export_image_get_path)
        self.file_menu_bar_import_tactool_csv.triggered.connect(self.import_tactool_csv_get_path)
        self.file_menu_bar_export_tactool_csv.triggered.connect(self.export_tactool_csv_get_path)
        self.menu_bar_recoordinate_csv.triggered.connect(self.toggle_recoordinate_dialog)

        # Connect button clicks to handlers
        self.clear_points_button.clicked.connect(self.clear_analysis_points)
        self.reset_ids_button.clicked.connect(lambda: self.reload_analysis_points(transform=reset_id))
        self.reset_settings_button.clicked.connect(self.reset_settings)
        self.colour_button.clicked.connect(self.set_point_colour)
        self.set_scale_button.clicked.connect(self.toggle_scaling_mode)

        # Connect Graphics View interactions to handlers
        self.graphics_view.left_click.connect(self.add_analysis_point)
        self.graphics_view.right_click.connect(self.remove_analysis_point)

        # Connect Table interaction clicks to handlers
        self.table_view.selected_analysis_point.connect(self.get_point_settings)
        self.table_model.invalid_label_entry.connect(self.show_message)
        self.table_model.updated_analysis_points.connect(self.reload_analysis_points)


    def create_status_bar_messages(self):
        """
        Function to create the status bar message functions.
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
        Function to toggle all of the status bar messages.
        """
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
        path = pyqt_open_dialog[0]
        if path:
            try:
                self.graphics_view.load_image(path)
                self.image_filepath = path
                self.setWindowTitle(f"TACtool: {self.image_filepath}")
            except Exception as error:
                self.data_error_message(error)


    def export_image_get_path(self) -> None:
        """
        Function to create a PyQt File Dialog, allowing the user to visually select a directory to export an image file.
        """
        if self.validate_current_data(validate_image=True):
            filepath = self.image_filepath if self.image_filepath else ""
            pyqt_save_dialog = QFileDialog.getSaveFileName(
                parent=self,
                caption="Export Image",
                directory=filepath,
                filter=self.default_settings["image_format"],
            )
            path = pyqt_save_dialog[0]
            if path:
                try:
                    self.graphics_view.save_image(path)
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
        path = pyqt_open_dialog[0]
        if path:
            try:
                self.load_tactool_csv_data(path)
                self.csv_filepath = path
            except Exception as error:
                self.data_error_message(error)


    def load_tactool_csv_data(self, filepath: str) -> None:
        """
        Load the Analysis Point data from a given CSV file and add it into the program.
        """
        try:
            analysis_points = parse_tactool_csv(filepath, self.default_settings)
            self.clear_analysis_points()
            self.reset_settings()
            for analysis_point in analysis_points:
                self.add_analysis_point(**analysis_point, from_click=False)
            self.table_view.scrollToTop()

        # A KeyError and UnicodeError usually occur with an incorrectly formatted CSV file
        except (KeyError, UnicodeError):
            # Show a message to the user informing them of which headers should be in the CSV file
            public_headers = [header for header in self.table_model.headers
                              if not header.startswith("_")]
            message = dedent(f"""
                There was an error when loading data from CSV file: {filepath.split("/")[-1]}.

                Must use csv with header {public_headers}.
            """)
            self.show_message("Error loading data", message, "warning")


    def export_tactool_csv_get_path(self) -> None:
        """
        Function to create a PyQt File Dialog,
        allowing the user to visually select a directory to save a TACtool CSV file.
        """
        if self.validate_current_data():
            filepath = self.csv_filepath if self.csv_filepath else ""
            pyqt_save_dialog = QFileDialog.getSaveFileName(
                parent=self,
                caption="Export as TACtool CSV",
                directory=filepath,
                filter=self.default_settings["csv_format"],
            )
            path = pyqt_save_dialog[0]
            if path:
                try:
                    self.table_model.export_csv(path)
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
        if self.status_bar_messages["ref_points"]["status"]:
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
        label: str = None,
        diameter: int = None,
        scale: float = None,
        colour: str = None,
        notes: str = "",
        apid: int = None,
        sample_name: str = "",
        mount_name: str = "",
        material: str = "",
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

        analysis_point = self.graphics_scene.add_analysis_point(
            x=x,
            y=y,
            label=label,
            diameter=diameter,
            scale=scale,
            colour=colour,
            notes=notes,
            apid=apid,
            sample_name=sample_name,
            mount_name=mount_name,
            material=material,
        )
        logger.debug("Created Analysis Point: %s", analysis_point)

        # Update the status bar messages and PyQt Table View
        self.toggle_status_bar_messages()
        self.table_view.model().layoutChanged.emit()


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
        # Save the existing Points before clearing them
        current_analysis_points = self.table_model.analysis_points
        self.clear_analysis_points()
        # Iterate through each previously existing Point and recreate it
        for analysis_point in current_analysis_points:
            analysis_point = transform(analysis_point)
            self.add_analysis_point(
                apid=analysis_point.id,
                x=analysis_point.x,
                y=analysis_point.y,
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


    def remove_analysis_point(self, x: int = None, y: int = None, apid: int = None) -> None:
        """
        Remove an Analysis Point from the PyQt Graphics Scene.
        The Point is specified using it's coordinates or it's ID value.
        """
        deletion_result = self.graphics_scene.remove_analysis_point(x=x, y=y, apid=apid)
        # If the deletion returned a value, it is the Analysis Point ID and so is outputted
        if deletion_result:
            logger.debug("Deleted Analysis Point: %s", deletion_result)

        # Update the status bar messages and PyQt TableView
        self.toggle_status_bar_messages()
        self.table_view.model().layoutChanged.emit()


    def set_point_colour(self) -> None:
        """
        Function to update the selected colour in the user interface.
        """
        # Create a PyQt Colour Dialog to select a colour
        colour = QColorDialog.getColor()
        if colour.isValid():
            # Update the colour of the button and the value
            # colour is a QColor class
            hex_colour = colour.name()
            self.point_colour = hex_colour
            self.set_colour_button_style()


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
            # Move the Set Scale Dialog box to be at the top left corner of the main window
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


    def toggle_main_input_widgets(self, enable: bool) -> None:
        """
        Toggle each of the input widgets in the main window to be enabled or disabled.
        """
        for widget in self.main_input_widgets:
            widget.setEnabled(enable)


    def set_scale(self, scale: float) -> None:
        """
        Function to set the scale of the program given when the Set scale button is clicked in the Set Scale dialog box.
        """
        self.scale_value_input.setText(str(scale))
        self.toggle_status_bar_messages()


    def get_point_settings(self, analysis_point: AnalysisPoint, clicked_column_index: int) -> None:
        """
        Function to get the settings of an Analysis Point which has been selected in the PyQt Table View.
        These settings are then updated to be the current settings.
        """
        logger.debug("Selected Analysis Point: %s", analysis_point)
        # If the column of the cell the user clicked is the id
        if clicked_column_index == self.table_model.headers.index("id"):
            # Update the Analysis Point settings to be the same as the Point settings of the Point selected in the table
            self.update_point_settings(
                sample_name=analysis_point.sample_name,
                mount_name=analysis_point.mount_name,
                material=analysis_point.material,
                label=analysis_point.label,
                diameter=analysis_point.diameter,
                scale=analysis_point.scale,
                colour=analysis_point.colour,
            )


    def reset_settings(self) -> None:
        """
        Function to reset input fields and general Analysis Point settings to default.
        """
        self.update_point_settings(
            sample_name=self.default_settings["metadata"],
            mount_name=self.default_settings["metadata"],
            material=self.default_settings["metadata"],
            label=self.default_settings["label"],
            diameter=self.default_settings["diameter"],
            scale=self.default_settings["scale"],
            colour=self.default_settings["colour"],
        )


    def update_point_settings(
        self,
        sample_name: str = None,
        mount_name: str = None,
        material: str = None,
        label: str = None,
        diameter: int = None,
        scale: str | float = None,
        colour: str = None,
    ) -> None:
        """
        Function to update the Analysis Point settings to be the given settings.
        If a value is given for a field, then the value and any corresponding
        User Interface elements are updated.
        """

        if sample_name is not None:
            self.sample_name_input.setText(sample_name)

        if mount_name is not None:
            self.mount_name_input.setText(mount_name)

        if material is not None:
            self.material_input.setText(material)

        if label is not None:
            self.label_input.setCurrentText(label)

        if diameter is not None:
            self.diameter_input.setValue(diameter)

        if scale is not None:
            self.scale_value_input.setText(str(scale))
            self.toggle_status_bar_messages()

        if colour is not None:
            self.point_colour = colour
            self.set_colour_button_style()


    def toggle_recoordinate_dialog(self) -> None:
        """
        Toggle the recoordination dialog window.
        """
        # If the program is not in recoordination mode
        if self.recoordinate_dialog is None:
            # Create the Set Scale Dialog box
            self.recoordinate_dialog = RecoordinateDialog(self.testing_mode)
            # Disable main window input widgets
            self.toggle_main_input_widgets(False)
            # Move the Set Scale Dialog box to be at the top left corner of the main window
            main_window_pos = self.pos()
            self.recoordinate_dialog.move(main_window_pos.x() + 50, main_window_pos.y() + 50)

            # Connect the Set Scale dialog buttons
            self.recoordinate_dialog.recoordinate_clicked.connect(self.recoordinate_points)
            self.recoordinate_dialog.closed_recoordinate_dialog.connect(self.toggle_recoordinate_dialog)
            self.recoordinate_dialog.invalid_path_entry.connect(self.show_message)

        # Else when the program is in recoordination mode, reset the Recoordination Dialog value
        else:
            self.recoordinate_dialog = None
            # Enable main window widgets
            self.toggle_main_input_widgets(True)


    def recoordinate_points(self, input_csv: str, output_csv: str):
        print("RECOORDINATE")
        print(input_csv)
        print(output_csv)


    def data_error_message(self, error: Exception) -> None:
        """
        Function to show an error message to the user in the event that
        an error occurs when loading in data.
        """
        self.show_message(
            "Error loading data",
            f"An unexpected error occured: {error}",
            "warning",
        )


    def show_message(self, title: str, message: str, type: str) -> bool:
        """
        Function to show a given message to the user in a PyQt QMessageBox.
        """
        # Creating the PyQt Message box and formatting it
        widget = QMessageBox()
        widget.setWindowTitle(title)
        widget.setText(message)
        widget.setStandardButtons(QMessageBox.Ok)

        # Setting the type of message
        if type == "warning":
            widget.setIcon(QMessageBox.Warning)
        elif type == "information":
            widget.setIcon(QMessageBox.Information)
        elif type == "question":
            widget.setIcon(QMessageBox.Question)
            widget.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)

        # Show the message box
        message_box = widget.exec_()
        # If the user presses the Cancel button on the message box
        if message_box == QMessageBox.Cancel:
            return False
        return True


    def closeEvent(self, event=None) -> None:
        """
        Function which is run by PyQt when the application is closed.
        """
        # Close any open dialogs
        dialogs = [
            self.recoordinate_dialog,
            self.set_scale_dialog,
        ]
        for dialog in dialogs:
            if dialog is not None:
                dialog.close()
