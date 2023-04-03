"""
The Graphics Scene manages elements which are painted onto images.
"""

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

from tactool.table_model import AnalysisPoint, TableModel


class GraphicsScene(QGraphicsScene):
    """
    PyQt QGraphicsScene with convenience functions for Analysis Point data.
    """
    def __init__(self) -> None:
        super().__init__()
        # _maximum_point_id is used to track the next incremental ID value available
        self._maximum_point_id = 0

        # Defining variables used in the Graphics Scene for scaling mode
        self.scaling_rect: Optional[QGraphicsRectItem] = None
        self.scaling_group: Optional[QGraphicsItemGroup] = None
        self.scaling_line: Optional[QGraphicsLineItem] = None

        self.table_model = TableModel()


    def add_analysis_point(
            self,
            x: int,
            y: int,
            label: str,
            diameter: int,
            colour: str,
            scale: float,
            notes: str = "",
            apid: int = None,
            sample_name: str = "",
            mount_name: str = "",
            material: str = "",
    ) -> AnalysisPoint:
        """
        Function to draw an Analysis Point onto the Graphics Scene and
        add it's data to the Table Model.
        """
        # Set the drawing colours to use the given colour
        # pen just provides an outline of an object
        # brush also fills the object
        pen = QPen(QColor(colour))
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

        # If no analysis point ID is given, assign it the next ID available
        # Else, the next available ID requires incrementing anyway due to
        # the additional point being added
        if not apid:
            apid = self.next_point_id
        else:
            _ = self.next_point_id

        # Set the label text of the point
        # Use the given label if there is one, else use the point ID
        label_text = f"{apid}_{label}" if label else str(apid)
        # Create the label as a PyQt graphic and set it's attributes appropriately
        label_text_item = QGraphicsTextItem(label_text)
        label_text_item.setPos(x, y)
        label_text_item.setDefaultTextColor(QColor(colour))
        label_text_item.setFont(QFont("Helvetica", 14))
        # Add the label to the Graphics Scene
        self.addItem(label_text_item)

        # Place the new point data into an Analysis Point object
        point_data = AnalysisPoint(
            apid,
            label,
            x,
            y,
            diameter,
            scale,
            colour,
            sample_name,
            mount_name,
            material,
            notes,
            outer_ellipse,
            inner_ellipse,
            label_text_item,
        )
        # Add the Analysis Point to the Table Model
        self.table_model.add_point(point_data)
        return point_data


    def remove_analysis_point(self, x: int, y: int, apid: int) -> Optional[int]:
        """
        Function to remove an Analysis Point from the Graphics Scene based on it's coordinates.
        """
        analysis_point = None
        # If a target ID is provided, get the Analysis Point using it's ID
        if apid:
            analysis_point = self.table_model.get_point_by_apid(apid)

        # Else when the user right clicks on the Graphics View to remove an Analysis Point
        elif x and y:
            # Get the ellipse and check it exists
            ellipse = self.get_ellipse_at(x, y)
            if ellipse:
                # Get the corresponding Analysis Point object of the ellipse
                analysis_point = self.table_model.get_point_by_ellipse(ellipse)

        # If an Analysis Point is found
        if analysis_point:
            self.table_model.remove_point(analysis_point.id)
            # Remove the ellipse elements from the PyQt Graphics Scene
            self.removeItem(analysis_point._outer_ellipse)
            self.removeItem(analysis_point._inner_ellipse)
            self.removeItem(analysis_point._label_text_item)
            return analysis_point.id


    def get_ellipse_at(self, x: int, y: int) -> Optional[QGraphicsEllipseItem]:
        """
        Function to get an Ellipse Item from the Graphics Scene at the given coordinates.
        """
        # Using list comprehension to iterate through the existing Analysis Points
        # Using PyQt QGraphicsScene selection functions to find the Analysis Points at the given coordinates
        # Only adding it to the list if it is an Ellipse item
        ellipse_items = [
            item for item in self.items(QRectF(x, y, 2, 2),
                                        Qt.ItemSelectionMode(Qt.IntersectsItemShape),
                                        Qt.SortOrder(Qt.DescendingOrder))
            if type(item) is QGraphicsEllipseItem
        ]

        # If there are items in the list, return the first as it will be the target ellipse
        return ellipse_items[0] if ellipse_items else None


    @property
    def next_point_id(self) -> int:
        """
        Function to iterate and return the maximum Analysis Point ID value.
        """
        self._maximum_point_id += 1
        return self._maximum_point_id


    def toggle_transparent_window(self, graphics_view_image: QGraphicsPixmapItem) -> None:
        """
        Function to toggle a transparent grey overlay ontop of the image when entering scaling mode.
        """
        if not self.scaling_rect:
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
        # Else there is currently a transparent PyQt Rect
        else:
            # Remove the PyQt Rect from the PyQt Item Group and reset the scaling_rect variable
            self.removeItem(self.scaling_rect)
            self.scaling_rect = None


    def draw_scale_line(self, start_point: float, end_point: float) -> None:
        """
        Function to draw or redraw the scale line when in scaling mode.
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
        Function to draw an ellipse at the given coordinates.
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
        Function to remove all items from the Graphics Scene associated with the scaling mode.
        """
        # If there are items in the PyQt Item Group for scaling items
        if self.scaling_group:
            # Iterate through the items and remove them if they are not
            # the transparet PyQt Rect, this is removed separately
            for item in self.scaling_group.childItems():
                if item != self.scaling_rect:
                    self.removeItem(item)
            # Reset the scaling_line variable
            self.scaling_line = None
