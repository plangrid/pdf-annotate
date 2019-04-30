from __future__ import division

from collections import namedtuple

from pdf_annotate.util.geometry import matrix_multiply
from pdf_annotate.util.geometry import transform_point
from pdf_annotate.util.geometry import transform_vector


ZERO_TOLERANCE = 0.00000000000001


class ContentStream(object):
    """An abstraction over a PDF content stream, e.g. (draw a green rectangle):
    '0 1 0 rg 3 w 1 1 2 2 re S'.

    This abstraction will allow users to draw more precise annotations, while
    still allowing this library to transform those annotations to be properly
    drawn in PDF user space. For instance, a user could do:

    content_stream = ContentStream([
        StrokeColor(1, 0, 0),
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
        return ContentStream([
            command.transform(transform) for command in self.commands
        ])

    def resolve(self):
        return ' '.join(
            command.resolve() for command in self.commands
        )

    @staticmethod
    def join(stream1, stream2):
        """Combine two content streams."""
        return ContentStream(stream1.commands + stream2.commands)


class BaseCommand(object):
    COMMAND = ''

    def transform(self, t):
        return self

    def resolve(self):
        return self.COMMAND


class StrokeColor(namedtuple('Stroke', ['r', 'g', 'b']), BaseCommand):
    COMMAND = 'RG'

    def resolve(self):
        return '{} {} {} {}'.format(
            format_number(self.r),
            format_number(self.g),
            format_number(self.b),
            self.COMMAND
        )


class StrokeWidth(namedtuple('StrokeWidth', ['width']), BaseCommand):
    COMMAND = 'w'

    def resolve(self):
        return '{} {}'.format(format_number(self.width), self.COMMAND)


class FillColor(namedtuple('Fill', ['r', 'g', 'b']), BaseCommand):
    COMMAND = 'rg'

    def resolve(self):
        return '{} {} {} {}'.format(
            format_number(self.r),
            format_number(self.g),
            format_number(self.b),
            self.COMMAND
        )


class BeginText(BaseCommand):
    COMMAND = 'BT'


class EndText(BaseCommand):
    COMMAND = 'ET'


class Stroke(BaseCommand):
    COMMAND = 'S'


class StrokeAndFill(BaseCommand):
    COMMAND = 'B'


class Fill(BaseCommand):
    COMMAND = 'f'


class Save(BaseCommand):
    COMMAND = 'q'


class Restore(BaseCommand):
    COMMAND = 'Q'


class Close(BaseCommand):
    COMMAND = 'h'


class Font(namedtuple('Font', ['font', 'font_size']), BaseCommand):
    COMMAND = 'Tf'

    def resolve(self):
        return '/{} {} {}'.format(self.font, self.font_size, self.COMMAND)


class Text(namedtuple('Text', ['text']), BaseCommand):
    COMMAND = 'Tj'

    def resolve(self):
        return '({}) {}'.format(self.text, self.COMMAND)


class XObject(namedtuple('XObject', ['name']), BaseCommand):
    COMMAND = 'Do'

    def resolve(self):
        return '/{} {}'.format(self.name, self.COMMAND)


class GraphicsState(namedtuple('GraphicsState', ['name']), BaseCommand):
    COMMAND = 'gs'

    def resolve(self):
        return '/{} {}'.format(self.name, self.COMMAND)


class Rect(namedtuple('Rect', ['x', 'y', 'width', 'height']), BaseCommand):
    COMMAND = 're'

    def resolve(self):
        return '{} {} {} {} {}'.format(
            format_number(self.x),
            format_number(self.y),
            format_number(self.width),
            format_number(self.height),
            self.COMMAND
        )

    def transform(self, t):
        x, y = transform_point((self.x, self.y), t)
        width, height = transform_vector((self.width, self.height), t)
        return Rect(x, y, width, height)


class Move(namedtuple('Move', ['x', 'y']), BaseCommand):
    COMMAND = 'm'

    def resolve(self):
        return '{} {} {}'.format(
            format_number(self.x),
            format_number(self.y),
            self.COMMAND,
        )

    def transform(self, t):
        x, y = transform_point((self.x, self.y), t)
        return Move(x, y)


class Line(namedtuple('Line', ['x', 'y']), BaseCommand):
    COMMAND = 'l'

    def resolve(self):
        return '{} {} {}'.format(
            format_number(self.x),
            format_number(self.y),
            self.COMMAND,
        )

    def transform(self, t):
        x, y = transform_point((self.x, self.y), t)
        return Line(x, y)


class Bezier(namedtuple('Bezier', ['x1', 'y1', 'x2', 'y2', 'x3', 'y3']), BaseCommand):
    """Cubic bezier curve, from the current point to (x3, y3), using (x1, y1)
    and (x2, y2) as control points.
    """
    COMMAND = 'c'

    def resolve(self):
        formatted = [
            format_number(n) for n in
            (self.x1, self.y1, self.x2, self.y2, self.x3, self.y3)
        ]
        return '{} {} {} {} {} {} {}'.format(*formatted, self.COMMAND)

    def transform(self, t):
        x1, y1 = transform_point((self.x1, self.y1), t)
        x2, y2 = transform_point((self.x2, self.y2), t)
        x3, y3 = transform_point((self.x3, self.y3), t)
        return Bezier(x1, y1, x2, y2, x3, y3)


# also need Bezier y and v:
#  x2 y2 x3 y3 v --> current point is the first control point
#  x1 y1 x3 y3 y --> x3 y3 is the second control point


class CTM(namedtuple('CTM', ['matrix']), BaseCommand):
    COMMAND = 'cm'

    def resolve(self):
        return '{} {} {} {} {} {} {}'.format(
            *[format_number(n) for n in self.matrix],
            self.COMMAND,
        )

    def transform(self, t):
        return CTM(matrix_multiply(t, self.matrix))


class TextMatrix(namedtuple('TextMatrix', ['matrix']), BaseCommand):
    COMMAND = 'Tm'

    def resolve(self):
        return '{} {} {} {} {} {} {}'.format(
            *[format_number(n) for n in self.matrix],
            self.COMMAND,
        )

    def transform(self, t):
        return TextMatrix(matrix_multiply(t, self.matrix))


def format_number(n):
    # Really small numbers should just be rounded to 0
    if -ZERO_TOLERANCE <= n <= ZERO_TOLERANCE:
        return '0'
    # Cut off unnecessary decimals
    if n % 1 == 0:
        return str(int(n))
    # Otherwise return 10 decimal places, but remove trailing zeros. I wish I
    # could use 'g' for this, but that switches to scientific notation at
    # certain thresholds.
    string = '{:.10f}'.format(n)
    i = len(string) - 1
    while string[i] == '0':
        i -= 1
    return string[:i + 1]


def quadratic_to_cubic_bezier(
    start_x, start_y,
    control_x, control_y,
    end_x, end_y
):
    """Make a cubic bezier curve from the parameters of a quadratic bezier.

    This is necessary because PDF doesn't have quadratic beziers.
    """
    cp1x = start_x + 2 / 3 * (control_x - start_x)
    cp1y = start_y + 2 / 3 * (control_y - start_y)
    cp2x = end_x + 2 / 3 * (control_x - end_x)
    cp2y = end_y + 2 / 3 * (control_y - end_y)
    return Bezier(cp1x, cp1y, cp2x, cp2y, end_x, end_y)
