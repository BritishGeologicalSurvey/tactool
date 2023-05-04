"""
The Scale Dialog is used for allowing the user to see the new scale values.
They can then either reset the values, cancel them or continue with them.
"""

from PyQt5.QtCore import (
    pyqtSignal,
    Qt,
)
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class SetScaleDialog(QDialog):
    """
    PyQt QDialog class for creating the set scale dialog box when in scaling mode.
    """
    # Tracks when the Clear button is clicked
    clear_scale = pyqtSignal()
    # Tracks when the Set Scale button is clicked
    set_scale_clicked = pyqtSignal(float)
    # Tracks when the Set Scale Dialog Box is closed
    closed_set_scale_dialog = pyqtSignal()

    def __init__(self, testing_mode: bool) -> None:
        super().__init__()
        self.testing_mode = testing_mode

        # Setting default input value
        self.pixel_input_default = "Not Set"

        # Setting the Dialog Box settings
        self.setWindowTitle("Set Scale")
        self.setMinimumSize(100, 200)
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
        # Main buttons
        self.set_scale_button = QPushButton("OK", self)
        self.clear_scale_button = QPushButton("Clear", self)
        self.cancel_button = QPushButton("Cancel", self)

        # Distance label and input
        distance_label = QLabel("Distance (µm):")
        self.distance_input = QSpinBox()
        self.distance_input.setMaximum(100000)

        # Pixels label and input
        pixels_label = QLabel("Pixels:")
        self.pixel_input = QLineEdit()
        self.pixel_input.setText(self.pixel_input_default)
        self.pixel_input.setEnabled(False)

        # Scale label and input
        scale_label = QLabel("Scale (Pixels per µm):")
        self.scale_value = QLineEdit()
        self.scale_value.setValidator(QDoubleValidator())
        self.scale_value.setEnabled(False)

        # Arrange button layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignLeft)
        buttons_layout.addWidget(self.set_scale_button)
        buttons_layout.addWidget(self.clear_scale_button)
        buttons_layout.addWidget(self.cancel_button)

        # Arrange label and input boxes layout
        settings_widgets_layout = QVBoxLayout()
        settings_widgets_layout.addWidget(distance_label)
        settings_widgets_layout.addWidget(self.distance_input)
        settings_widgets_layout.addWidget(pixels_label)
        settings_widgets_layout.addWidget(self.pixel_input)
        settings_widgets_layout.addWidget(scale_label)
        settings_widgets_layout.addWidget(self.scale_value)

        # Arrange overall Set Scale Dialog box layout
        scale_dialog_layout = QVBoxLayout()
        scale_dialog_layout.addLayout(settings_widgets_layout)
        scale_dialog_layout.addLayout(buttons_layout)
        self.setLayout(scale_dialog_layout)


    def connect_signals_and_slots(self) -> None:
        """
        Function for connecting signals and slots of buttons and input boxes.
        """
        # Connect signals and slots for buttons
        self.set_scale_button.clicked.connect(self.set_scale)
        self.clear_scale_button.clicked.connect(self.clear_scale.emit)
        self.cancel_button.clicked.connect(self.closeEvent)

        # Connect signals and slots for input boxes
        self.distance_input.valueChanged.connect(self.update_scale)
        self.pixel_input.textChanged.connect(self.update_scale)


    def update_scale(self) -> tuple[float, float]:
        """
        Function to update the scale value in the Set Scale dialog box.
        """
        pixels = self.pixel_input.text()
        distance = float(self.distance_input.value()) if self.distance_input.value() else 0.0
        scale = ""
        # If the pixels value is not the default value and the distance is greater than 0
        if pixels != self.pixel_input_default and distance > 0:
            pixels = float(pixels)
            # Calculate the ratio difference as the new scale value
            # Scale value then represents the number of pixels per micron
            scale = round(pixels / distance, 2)
        # Update the scale value in the Set Scale Dialog box
        self.scale_value.setText(str(scale))
        return pixels, distance


    def scale_move_event_handler(self, pixel_distance: float) -> None:
        """
        Function to handle the change of a scale point on the PyQt Graphics Scene when in scaling mode.
        """
        # Set the pixel distance value in the Set Scale Dialog box
        self.pixel_input.setText(str(pixel_distance))


    def set_scale(self) -> None:
        """
        Function to update the scalue value in in the scale input box of the main window.
        """
        # If a scale value has been entered
        if self.scale_value.text():
            # Emit a signal that the set scale button has been clicked
            # passing the input value as a float
            self.set_scale_clicked.emit(float(self.scale_value.text()))
            self.closeEvent()


    def closeEvent(self, event=None) -> None:
        """
        Function which is run by PyQt when the application is closed.
        """
        self.closed_set_scale_dialog.emit()
