"""
Module for utilities and functions to help with development.
"""
import logging

import numpy as np
from PyQt5.QtCore import pyqtRemoveInputHook


def ipdb_breakpoint():
    """
    Drops code into IPYthon debugger.
    Press 'c' to continue running code.
    """
    import ipdb  # noqa - don't import at top level in case not installed

    # Switch off unwanted IPython loggers
    for lib in ('asyncio', 'parso'):
        logging.getLogger(lib).setLevel(logging.WARNING)

    pyqtRemoveInputHook()
    ipdb.set_trace()

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
+ https://medium.com/hipster-color-science/computing-2d-affine-transformations-using-only-matrix-multiplication-2ccb31b52181
"""
def affine_transform_matrix(source: list[tuple[float, float]],
                            dest: list[tuple[float, float]]) -> np.ndarray:
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


def affine_transform_point(matrix: np.ndarray,
                           point: tuple[float, float]) -> tuple[float, float]:
    """Apply an affine transformation to a 2D point"""
    # Convert the source point to 3D NumPy array
    # Adding z=1 makes point "homogeneous"
    src = np.array([*point, 1])

    # Apply the affine transformation
    dest = matrix @ src
    dest = (int(dest[0]), int(dest[1]))  # to 2D integer coordinate

    return dest
