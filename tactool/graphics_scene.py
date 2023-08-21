from typing import Optional

from PyQt5.QtCore import (
    Qt,
    QLineF,
    QRectF,
)
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPen,
)
from PyQt5.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItemGroup,
    QGraphicsLineItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
)

from tactool.analysis_point import AnalysisPoint
from tactool.utils import LoggerMixin


class GraphicsScene(QGraphicsScene, LoggerMixin):
    """
    PyQt QGraphicsScene with convenience functions for Analysis Point data.
    Manages elements which are painted onto images.
    """
    def __init__(self) -> None:
        super().__init__()

        # Defining variables used in the Graphics Scene for scaling mode
        self.scaling_rect: Optional[QGraphicsRectItem] = None
        self.scaling_group: Optional[QGraphicsItemGroup] = None
        self.scaling_line: Optional[QGraphicsLineItem] = None


    def add_analysis_point(
        self,
        x: int,
        y: int,
        apid: int,
        label: str,
        diameter: int,
        colour: str,
        scale: float,
        ghost: bool = False,
    ) -> tuple[QGraphicsEllipseItem, QGraphicsEllipseItem, QGraphicsTextItem]:
        """
        Draw an Analysis Point onto the Graphics Scene.
        Returns the newly created graphics items.
        """
        # The alpha changes for ghost points
        if ghost:
            alpha = 100
        else:
            alpha = 200
            self.logger.debug("Adding new Analysis Point")

        # Set the drawing colours to use the given colour
        # pen just provides an outline of an object
        # brush also fills the object
        qcolour = QColor(colour)
        qcolour.setAlpha(alpha)
        pen = QPen(qcolour)
        brush = QBrush(pen.color())

        # Calculate the scaled diameter size in pixels based on the given scale
        ellipse_diameter = diameter * scale
        # Draw the inner ellipse, it remains the same size regardless of scale
        inner_ellipse = self.addEllipse(
            x,
            y,
            1,
            1,
            pen,
            brush,
        )
        # Draw the outer ellipse, it changes size with the given scale
        pen.setWidth(4)
        outer_ellipse = self.addEllipse(
            x - (ellipse_diameter // 2),
            y - (ellipse_diameter // 2),
            ellipse_diameter,
            ellipse_diameter,
            pen,
        )

        # Set the label text of the point
        # Use the given label if there is one, else use the point ID
        label_text = f"{apid}_{label}" if label else str(apid)
        # Create the label as a PyQt graphic and set it's attributes appropriately
        label_text_item = QGraphicsTextItem(label_text)
        label_text_item.setPos(x, y)
        label_text_item.setDefaultTextColor(qcolour)
        label_text_item.setFont(QFont("Helvetica", 14))
        # Add the label to the Graphics Scene
        self.addItem(label_text_item)

        return outer_ellipse, inner_ellipse, label_text_item


    def remove_analysis_point(
        self,
        ap: AnalysisPoint,
        log: bool = True,
    ) -> None:
        """
        Remove the QGraphics items belonging to the given AnalysisPoint from the GraphicsScene.
        """
        if log:
            self.logger.debug("Removing graphics items for analysis point ID: %s", ap.id)
        for item in [ap._inner_ellipse, ap._outer_ellipse, ap._label_text_item]:
            self.removeItem(item)


    def get_ellipse_at(self, x: int, y: int) -> Optional[QGraphicsEllipseItem]:
        """
        Get an Ellipse Item from the Graphics Scene at the given coordinates.
        """
        # Using PyQt QGraphicsScene selection functions to find the Analysis Points at the given coordinates
        # Only adding it to the list if it is an Ellipse item
        ellipse_items = [
            item
            for item in self.items(
                QRectF(x, y, 2, 2),
                Qt.ItemSelectionMode(Qt.IntersectsItemShape),
                Qt.SortOrder(Qt.DescendingOrder),
            )
            if isinstance(item, QGraphicsEllipseItem)
        ]

        # If there are items in the list, return the first as it will be the target ellipse
        return ellipse_items[0] if ellipse_items else None


    def toggle_transparent_window(self, graphics_view_image: QGraphicsPixmapItem) -> None:
        """
        Toggle a transparent grey overlay ontop of the image for scaling mode.
        """
        if self.scaling_rect is not None:
            self.logger.debug("Removing transparent window")
            # Remove the PyQt Rect from the PyQt Item Group and reset the scaling_rect variable
            self.removeItem(self.scaling_rect)
            self.scaling_rect = None
        else:
            self.logger.debug("Adding transparent window")
            # Convert the current image to a pixmap
            image_pixmap = graphics_view_image.pixmap()
            image_width, image_height = image_pixmap.width(), image_pixmap.height()
            # Create a PyQt Rect Item matching the size of the current image
            self.scaling_rect = QGraphicsRectItem(QRectF(0, 0, image_width, image_height))
            # Set the Rect Item to be 50% transparent and grey in colour
            self.scaling_rect.setOpacity(0.5)
            self.scaling_rect.setBrush(Qt.gray)

            # Creating a PyQt Item Group to store all Graphics Scene scaling items within one variable
            self.scaling_group = self.createItemGroup([])
            self.scaling_group.addToGroup(self.scaling_rect)


    def draw_scale_line(self, start_point: float, end_point: float) -> None:
        """
        Draw or redraw the scale line when in scaling mode.
        """
        # If there is current a line, then remove it from the PyQt Item Group and
        # reset the scaling_line variable
        if self.scaling_line:
            self.removeItem(self.scaling_line)
            self.scaling_line = None

        # Create a PyQt Line and then transform it into a PyQt Graphics Line Item
        line = QLineF(start_point, end_point)
        self.scaling_line = QGraphicsLineItem(line)

        # Set the drawing mode to use a PyQt Pen in red
        self.scaling_line.setPen(QPen(QColor(Qt.red)))
        # Draw the line on the Graphics Scene
        line.setP2(end_point)
        self.scaling_line.setLine(line)
        # Add the line to the PyQt Item Group for scaling items
        self.scaling_group.addToGroup(self.scaling_line)


    def draw_scale_point(self, x: int, y: int) -> None:
        """
        Draw an ellipse at the given coordinates.
        Used for drawing small ellipse' at both ends of the scaling line.
        """
        # Set the drawing mode to use a PyQt Pen in red
        brush = QBrush(QPen(QColor(Qt.red)).color())
        # Draw a small ellipse at the given coordinates with a size of 3.0
        ellipse = QGraphicsEllipseItem(x - 1, y - 1, 3.0, 3.0)
        ellipse.setBrush(brush)
        # Add the ellipse to the PyQt Item Group for the scaling items
        self.scaling_group.addToGroup(ellipse)


    def remove_scale_items(self) -> None:
        """
        Remove all items from the Graphics Scene associated with the scaling mode.
        """
        self.logger.debug("Removing scaling items")
        # If there are items in the PyQt Item Group for scaling items
        if self.scaling_group:
            # Iterate through the items and remove them if they are not
            # the transparet PyQt Rect, this is removed separately
            for item in self.scaling_group.childItems():
                if item != self.scaling_rect:
                    self.removeItem(item)
            # Reset the scaling_line variable
            self.scaling_line = None
