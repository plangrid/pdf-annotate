from pdf_annotate.appearance import Appearance


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
