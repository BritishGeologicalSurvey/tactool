import argparse
import sys

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from tactool.graphics_scene import GraphicsScene
from tactool.graphics_view import GraphicsView
from tactool.recoordinate_dialog import RecoordinateDialog
from tactool.set_scale_dialog import SetScaleDialog
from tactool.table_model import TableModel
from tactool.table_view import TableView
from tactool.window import Window


class TACtool(QApplication):
    """
    PyQt QApplication class with references to high-level components.
    Includes some convenience property methods to aid with testing.
    """
    def __init__(
        self,
        args,
        developer_mode: bool = False,
        testing_mode: bool = False,
    ) -> None:
        super().__init__(args)
        self.testing_mode = testing_mode
        self.window = Window(self.testing_mode)

        if developer_mode:
            self.developer_mode()

        # In testing mode, the window is not displayed
        if testing_mode:
            self.window.setAttribute(Qt.WA_DontShowOnScreen, True)
        # In standard mode, show the window and execute the application
        else:
            self.window.showMaximized()
            sys.exit(self.exec())


    def developer_mode(self) -> None:
        """
        Start the program in developer mode.
        """
        # Preload an image into the program
        path = "test/data/test_cl_montage.png"
        self.window.image_filepath = path
        self.window.setWindowTitle(f"TACtool: {self.window.image_filepath}")
        self.graphics_view.load_image(path)
        # This shows the entirety of a preloaded image in the Graphics View during initialisation
        self.graphics_view.setTransform(QtGui.QTransform())


    @property
    def graphics_view(self) -> GraphicsView:
        return self.window.graphics_view

    @property
    def graphics_scene(self) -> GraphicsScene:
        return self.window.graphics_scene

    @property
    def table_model(self) -> TableModel:
        return self.window.table_model

    @property
    def table_view(self) -> TableView:
        return self.window.table_view

    @property
    def set_scale_dialog(self) -> SetScaleDialog:
        return self.window.set_scale_dialog

    @property
    def recoordinate_dialog(self) -> RecoordinateDialog:
        return self.window.recoordinate_dialog


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Application for annotating images with analysis points.")
    parser.add_argument(
        "--dev",
        default=False,
        action="store_true",
        help="Developer mode",
    )
    args = parser.parse_args()

    tactool_application = TACtool(sys.argv, args.dev)
