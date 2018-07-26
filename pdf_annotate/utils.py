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


def rotate_matrix(matrix, degrees):
    """Rotate matrix by degrees.

    :params list matrix: 6-item list representing common transformation matrix
    :params int degrees: integer degrees
    :returns list: matrix rotated by degrees, 6-item list
    """
    radians = to_radians(degrees)
    return [
        math.cos(radians),
        math.sin(radians),
        -math.sin(radians),
        math.cos(radians),
        matrix[4],
        matrix[5],
    ]


def translate(x, y):
    return [1, 0, 0, 1, x, y]


def identity():
    return [1, 0, 0, 1, 0, 0]
