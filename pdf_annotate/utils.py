# -*- coding: utf-8 -*-
import math

import six


def normalize_rotation(rotate):
    if rotate % 90:
        raise ValueError('Invalid Rotate value: {}'.format(rotate))
    while rotate < 0:
        rotate += 360
    while rotate >= 360:
        rotate -= 360
    return rotate


def is_numeric(v):
    return isinstance(v, six.integer_types + (float,))


def to_radians(degrees):
    return degrees * math.pi / 180


def rotate(degrees):
    """Return a homogenous rotation matrix by degrees

    :params int degrees: integer degrees
    :returns list: matrix rotated by degrees, 6-item list
    """
    radians = to_radians(degrees)
    return [
        math.cos(radians),
        math.sin(radians),
        -math.sin(radians),
        math.cos(radians),
        0,
        0,
    ]


def translate(x, y):
    return [1, 0, 0, 1, x, y]


def scale(x_scale, y_scale):
    return [x_scale, 0, 0, y_scale, 0, 0]


def identity():
    return [1, 0, 0, 1, 0, 0]


def matrix_multiply(A, B):
    """Multiply A by B. Both A and B are 6-item lists, which represent matrices
    in homogenous coordinates. The result is another 6-item list.

    If M is [a b c d e f], this represents the homogenous matrix of

        a b 0
        c d 0
        e f 1
    """
    a00, a01, a10, a11, a20, a21 = A
    a02, a12, a22 = 0, 0, 1

    b00, b01, b10, b11, b20, b21 = B
    b02, b12, b22 = 0, 0, 1

    # We don't have to compute all entries of the new matrix during
    # multiplication, since any multiple of affine transformations is an affine
    # transformation, and therefore homogenous coordinates.
    c00 = b00 * a00 + b01 * a10 + b02 * a20
    c01 = b00 * a01 + b01 * a11 + b02 * a21

    c10 = b10 * a00 + b11 * a10 + b12 * a20
    c11 = b10 * a01 + b11 * a11 + b12 * a21

    c20 = b20 * a00 + b21 * a10 + b22 * a20
    c21 = b20 * a01 + b21 * a11 + b22 * a21

    return [c00, c01, c10, c11, c20, c21]


def transform_point(point, matrix):
    """Transform point by matrix.

    :param list point: 2-item list
    :param list matrix: 6-item list representing transformation matrix
    :returns list: 2-item transformed point
    """
    x, y = point
    a, b, c, d, e, f = matrix
    # This leaves out some unnecessary stuff from the fact that the matrix is
    # homogenous coordinates.
    new_x = x * a + y * c + e
    new_y = x * b + y * d + f
    return [new_x, new_y]
