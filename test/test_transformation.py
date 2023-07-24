"""
Tests for functions in the transformation module
"""
import numpy as np
import pytest

from tactool.analysis_point import (
    affine_transform_point,
    affine_transform_matrix,
)

X_PLUS_10 = np.array([[1, 0, 10],
                      [0, 1, 0],
                      [0, 0, 1]])

Y_PLUS_10 = np.array([[1, 0, 0],
                      [0, 1, 10],
                      [0, 0, 1]])

SCALE_BY_2ish = np.array([[2.1, 0, 0],
                          [0, 2.1, 0],
                          [0, 0, 1]])


@pytest.mark.parametrize('matrix, src, expected', [
    (X_PLUS_10, (1, 1), (11, 1)),
    (X_PLUS_10, (1, 0), (11, 0)),
    (X_PLUS_10, (0, 1), (10, 1)),
    (Y_PLUS_10, (1, 1), (1, 11)),
    (Y_PLUS_10, (1, 0), (1, 10)),
    (Y_PLUS_10, (0, 1), (0, 11)),
    (SCALE_BY_2ish, (1, 1), (2, 2)),  # should round to nearest int
    (SCALE_BY_2ish, (10, 10), (21, 21)),  # no rounding required
])
def test_affine_transform_point(matrix, src, expected):
    # Act
    transformed = affine_transform_point(matrix, src)

    # Assert
    assert transformed == expected


def test_affine_transform_matrix():
    # Arrange
    src = [(0, 0), (1, 0), (1, 1), (0, 1)]
    dest = [(2, 2), (3, 2), (3, 3), (2, 3)]
    expected = np.array([
        [1, 0, 2],
        [0, 1, 2],
        [0, 0, 1]
    ])

    # Act
    matrix = affine_transform_matrix(src, dest)

    # Assert
    np.testing.assert_array_almost_equal(matrix, expected, decimal=10)
