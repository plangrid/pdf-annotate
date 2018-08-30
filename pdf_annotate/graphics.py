from collections import namedtuple

from pdf_annotate.appearance import Appearance
from pdf_annotate.utils import transform_point
from pdf_annotate.utils import transform_vector


ZERO_TOLERANCE = 0.00000000000001


class ContentStream(object):
    """An abstraction over a PDF content stream, e.g. (draw a green rectangle):
    '0 1 0 rg 3 w 1 1 2 2 re S'.

    This abstraction will allow users to draw more precise annotations, while
    still allowing this library to transform those annotations to be properly
    drawn in PDF user space. For instance, a user could do:

    content_stream = ContentStream([
        StrokeColor([1, 0, 0]),
        StrokeWidth(5),
        Move(10, 10),
        Line(20, 20),
        Stroke(),
    ])
    annotator.add_annotation(
        'square',
        location=Location(10, 10, 20, 20, page=0),
        appearance=Appearance(appearance_stream=content_stream),
    )

    This would draw a "square" annotation as a line, which is kind of silly,
    but it show the flexibility for the user to draw more complex annotations.
    Behind the scenes, the pdf-annotator library transforms the Move and Line
    operations to be properly placed in PDF user space.
    """

    def __init__(self, commands=None):
        self.commands = commands or []

    def add(self, command):
        self.commands.append(command)

    def extend(self, commands):
        self.commands.extend(commands)

    def transform(self, transform):
        return [
            command.transform(transform) for command in self.commands
        ]

    def resolve(self):
        return ' '.join(
            command.resolve() for command in self.commands
        )


class NoOpTransformBase(object):
    def transform(self, t):
        return self


class StaticCommand(NoOpTransformBase):
    def resolve(self):
        return self.COMMAND


class Rect(namedtuple('Rect', ['x', 'y', 'width', 'height'])):
    def resolve(self):
        return '{} {} {} {} re'.format(self.x, self.y, self.width, self.height)

    def transform(self, t):
        x, y = transform_point((self.x, self.y), t)
        width, height = transform_vector((self.width, self.height), t)
        return Rect(x, y, width, height)


class StrokeColor(namedtuple('Stroke', ['r', 'g', 'b']), NoOpTransformBase):
    def resolve(self):
        return '{} {} {} RG'.format(self.r, self.g, self.b)


class StrokeWidth(namedtuple('StrokeWidth', ['width']), NoOpTransformBase):
    def resolve(self):
        return '{} w'.format(self.width)


class FillColor(namedtuple('Fill', ['r', 'g', 'b']), NoOpTransformBase):
    def resolve(self):
        return '{} {} {} rg'.format(self.r, self.g, self.b)


class BeginText(StaticCommand):
    COMMAND = 'BT'


class EndText(StaticCommand):
    COMMAND = 'ET'


class Stroke(StaticCommand):
    COMMAND = 'S'


class StrokeAndFill(StaticCommand):
    COMMAND = 'B'


class Fill(StaticCommand):
    COMMAND = 'f'


class Save(StaticCommand):
    COMMAND = 'q'


class Restore(StaticCommand):
    COMMAND = 'Q'


class Close(StaticCommand):
    COMMAND = 'h'


class Move(namedtuple('Move', ['x', 'y'])):
    def resolve(self):
        return '{} {} m'.format(self.x, self.y)

    def transform(self, t):
        x, y = transform_point((self.x, self.y), t)
        return Move(x, y)


class Line(namedtuple('Line', ['x', 'y'])):
    def resolve(self):
        return '{} {} l'.format(self.x, self.y)

    def transform(self, t):
        x, y = transform_point((self.x, self.y), t)
        return Line(x, y)


class Bezier(namedtuple('Bezier', ['x1', 'y1', 'x2', 'y2', 'x3', 'y3'])):
    def resolve(self):
        return '{} {} {} {} {} {} c'.format(
            self.x1, self.y1,
            self.x2, self.y2,
            self.x3, self.y3,
        )

    def transform(self, t):
        x1, y1 = transform_point((self.x1, self.y1), t)
        x2, y2 = transform_point((self.x2, self.y2), t)
        x3, y3 = transform_point((self.x3, self.y3), t)
        return Bezier(x1, y1, x2, y2, x3, y3)


class Font(namedtuple('Font', ['font', 'font_size']), NoOpTransformBase):
    def resolve(self):
        return '/{} {} Tf'.format(self.font, self.font_size)


class CTM(namedtuple('CTM', ['matrix']), NoOpTransformBase):
    def resolve(self):
        return '{} {} {} {} {} {} cm'.format(
            *[format_number(n) for n in self.matrix]
        )


class TextMatrix(namedtuple('TextMatrix', ['matrix']), NoOpTransformBase):
    def resolve(self):
        return '{} {} {} {} {} {} Tm'.format(
            *[format_number(n) for n in self.matrix]
        )


class Text(namedtuple('Text', ['text']), NoOpTransformBase):
    def resolve(self):
        return '({}) Tj'.format(self.text)


def resolve_appearance_stream(A, transform):
    a = A.appearance_stream
    if a is None or isinstance(a, str):
        return A
    elif not isinstance(a, ContentStream):
        raise ValueError(
            'Invalid appearance stream format: {}'.format(type(a)))

    new_appearance = A.copy()
    new_appearance.appearance_stream = a.transform(transform).resolve()
    return new_appearance


def set_appearance_state(stream, A):
    """Update the graphics command stream to reflect appearance properties.

    :param ContentStream stream: current content stream
    :param Appearance A: appearance object
    """
    stream.extend([
        StrokeColor(*A.stroke_color),
        StrokeWidth(A.stroke_width),
    ])
    # TODO support more color spaces - CMYK and GrayScale
    if A.fill is not Appearance.TRANSPARENT and A.fill is not None:
        stream.add(FillColor(*A.fill))


def stroke_or_fill(stream, A):
    if A.fill is not Appearance.TRANSPARENT and A.fill is not None:
        stream.add(StrokeAndFill())
    else:
        stream.add(Stroke())


def format_number(n):
    # Really small numbers should just be rounded to 0
    if -ZERO_TOLERANCE <= n <= ZERO_TOLERANCE:
        return '0'
    # Cut off unnecessary decimals
    if n % 1 == 0:
        return str(int(n))
    # Otherwise return 10 decimal places
    return '{:.10f}'.format(n)
