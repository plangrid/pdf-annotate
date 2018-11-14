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


def matrix_multiply(*args):
    """Multiply a series of matrices. len(args) must be at least two. If more
    than two matrices are specified, the multiplications are chained, with the
    left-most matrices being multiplied first.

    E.g. matrix_multiply(A, B, C) => (A*B)*C

    Each matrix is a 6-item homogenous matrix.
    """
    if len(args) < 2:
        raise ValueError('Cannot multiply less than two matrices')
    r = _matrix_multiply(args[0], args[1])
    for m in args[2:]:
        r = _matrix_multiply(r, m)
    return r


def _matrix_multiply(A, B):
    a00, a01, a10, a11, a20, a21 = A

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


def transform_vector(vector, matrix):
    """Transform a vector by a matrix. This is similar to transform_point,
    except that translation isn't honored. Think of a vector as displacement in
    space, and a point as, well, a point in space.

    :param list vector: 2-item list
    :param list matrix: 6-item list representing transformation matrix
    :returns list: 2-item transformed point
    """
    x, y = vector
    a, b, c, d, _, _ = matrix
    new_x = x * a + y * c
    new_y = x * b + y * d
    return [new_x, new_y]


def unshift_token(text):
    """Remove a token from the front of a string.

    :param str text:
    :returns: {'text': str, 'separator': str, 'remainder': str}
    """
    if len(text) == 0:
        return {'text': text, 'separator': '', 'remainder': ''}

    token = ''
    for i in range(0, len(text)):
        char = text[i]
        if (char == ' ' and (len(token) >= 1 and token[i - 1] == ' ')):
            token += char
        elif (char == ' ' and len(token) == 0):
            token += char
        elif char == ' ':
            return {'text': token, 'separator': ' ', 'remainder': text[i + 1:]}
        elif char == '\n':
            return {
                'text': token,
                'separator': '\n',
                'remainder': text[i + 1:],
            }
        elif (len(token) >= 1 and token[i - 1] == ' '):
            return {
                'text': token,
                'separator': '',
                'remainder': text[len(token):],
            }
        else:
            token += char

    return {'text': token, 'separator': '', 'remainder': ''}


def unshift_line(text, measure, max_length):
    """Remove a line of text from a string.

    :param str text: text to be broken
    :param func measure: function that takes a string and returns its width
    :param int max_length: max width of each line
    :returns: {'text': str, 'remainder': str}
    """
    line = ''
    token = {'text': '', 'separator': '', 'remainder': text}
    while True:
        token = unshift_token(token['remainder'])
        token_text = token['text']
        remainder = token['remainder']
        separator = token['separator']
        if len(line) == 0:
            if len(token_text) > 0:
                # This allows us to add partial tokens for the first token
                for char in token_text:
                    if measure(line + char) > max_length:
                        line = char if len(line) == 0 else line
                        return {
                            'text': line,
                            'remainder': text[len(line):],
                        }
                    else:
                        line += char
                if separator == '\n':
                    return {'text': line, 'remainder': remainder}

                line += separator
            else:
                return {
                    'text': line,
                    'remainder': text[len(line) + len(separator):],
                }
        else:
            if measure(line + token_text) <= max_length:
                line += token_text
                if separator == '\n' or remainder == '':
                    return {'text': line, 'remainder': remainder}
                else:
                    line += separator
            else:
                return {'text': line, 'remainder': text[len(line):]}


def get_wrapped_lines(text, measure, max_length):
    """Break a string of text into lines wrapped to max_length.

    The algorithm is the same one used in the PGBS TextElement in web-viewer,
    to maintain consistency in line breaks.

    :param str text: text to be broken
    :param func measure: function that takes a string and returns its width
    :param int max_length: max width of each line
    :returns: list of strings
    """
    line = unshift_line(text, measure, max_length)
    lines = [line['text']]
    while (len(line['remainder']) > 0):
        line = unshift_line(line['remainder'], measure, max_length)
        lines.append(line)
    return [line['text'] for line in lines]
