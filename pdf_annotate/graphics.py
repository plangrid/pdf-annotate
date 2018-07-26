from pdf_annotate.appearance import Appearance


ZERO_TOLERANCE = 0.00000000000001


def set_appearance_state(stream, A):
    """Update the graphics command stream to reflect appearance properties.

    :param StringIO stream: current string of graphics state
    :param Appearance A: appearance object
    """
    stream.write('{} {} {} RG '.format(*A.stroke_color))
    stream.write('{} w '.format(A.stroke_width))
    # TODO support more color spaces - CMYK and GrayScale
    if A.fill is not Appearance.TRANSPARENT and A.fill is not None:
        stream.write('{} {} {} rg '.format(*A.fill))


def stroke(stream):
    stream.write('S ')


def stroke_or_fill(stream, A):
    if A.fill is not Appearance.TRANSPARENT and A.fill is not None:
        stream.write('B ')
    else:
        stroke(stream)


def save(stream):
    stream.write('q ')


def restore(stream):
    stream.write('Q ')


def format_number(n):
    # Really small numbers should just be rounded to 0
    if -ZERO_TOLERANCE <= n <= ZERO_TOLERANCE:
        return '0'
    # Cut off unnecessary decimals
    if n % 1 == 0:
        return str(int(n))
    # Otherwise return 10 decimal places
    return '{:.10f}'.format(n)


def set_cm(stream, matrix):
    stream.write(' '.join([format_number(v) for v in matrix]))
    stream.write(' cm ')


def set_tm(stream, matrix):
    stream.write(' '.join([str(v) for v in matrix]))
    stream.write(' Tm ')
