"""
Tests for functions in the utils module
"""
import numpy as np
import pytest

from tactool.utils import affine_transform_point

X_PLUS_10 = np.array([[1, 0, 10],
                      [0, 1, 0],
                      [0, 0, 1]])

Y_PLUS_10 = np.array([[1, 0, 0],
                      [0, 1, 10],
                      [0, 0, 1]])


@pytest.mark.parametrize('matrix, src, expected', [
    (X_PLUS_10, (1, 1), (11, 1)),
    (X_PLUS_10, (1, 0), (11, 0)),
    (X_PLUS_10, (0, 1), (10, 1)),
    (Y_PLUS_10, (1, 1), (1, 11)),
    (Y_PLUS_10, (1, 0), (1, 10)),
    (Y_PLUS_10, (0, 1), (0, 11)),
])
def test_affine_transform_point(matrix, src, expected):
    # Act
    transformed = affine_transform_point(matrix, src)

    # Assert
    assert transformed == expected