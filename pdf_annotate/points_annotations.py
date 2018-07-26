from six import StringIO

from pdf_annotate.annotations import Annotation
from pdf_annotate.annotations import make_border_dict
from pdf_annotate.graphics import set_appearance_state
from pdf_annotate.graphics import stroke
from pdf_annotate.graphics import stroke_or_fill
from pdf_annotate.utils import translate


def flatten_points(points):
    return [v for point in points for v in point]


class PointsAnnotation(Annotation):
    """An abstract annotation that defines its location on the document with
    an array of points.
    """
    @staticmethod
    def scale(location, scale):
        x_scale, y_scale = scale
        l = location.copy()
        points = [[x * x_scale, y * y_scale] for x, y in location.points]
        l.points = points
        return l

    @staticmethod
    def rotate(location, rotate, page_size):
        if rotate == 0:
            return location

        l = location.copy()

        if rotate == 90:
            width = page_size[1]
            points = [[width - y, x] for x, y in location.points]
        elif rotate == 180:
            width, height = page_size
            points = [[width - x, height - y] for x, y in location.points]
        else:
            height = page_size[0]
            points = [[y, height - x] for x, y in location.points]

        l.points = points
        l.rotation = rotate

        return l

    def make_rect(self):
        L = self._location
        stroke_width = self._appearance.stroke_width
        p = L.points[0]
        min_x, max_x, min_y, max_y = p[0], p[1], p[0], p[1]
        for x, y in L.points:
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
        return [
            min_x - stroke_width,
            min_y - stroke_width,
            max_x + stroke_width,
            max_y + stroke_width,
        ]

    def get_matrix(self):
        # Note: Acrobat and BB put padding that's not quite the same as the
        # stroke width here. I'm not quite sure why yet, so I'm not changing it.
        rect = self.make_rect()
        return translate(-rect[0], -rect[1])

    def base_points_object(self):
        obj = self.make_base_object()
        obj.BS = make_border_dict(self._appearance)
        obj.C = self._appearance.stroke_color
        obj.AP = self.make_ap_dict()
        # TODO line endings, leader lines, captions
        return obj


class Line(PointsAnnotation):
    subtype = 'Line'

    def graphics_commands(self):
        A = self._appearance
        points = self._location.points

        stream = StringIO()
        set_appearance_state(stream, A)
        stream.write('{} {} m '.format(points[0][0], points[0][1]))
        stream.write('{} {} l '.format(points[1][0], points[1][1]))
        stroke_or_fill(stream, A)

        return stream.getvalue()

    def as_pdf_object(self):
        obj = self.base_points_object()
        obj.L = flatten_points(self._location.points)
        # TODO line endings, leader lines, captions
        return obj


class Polygon(PointsAnnotation):
    subtype = 'Polygon'
    versions = ('1.5', '1.6', '1.7')

    def graphics_commands(self):
        A = self._appearance
        points = self._location.points

        stream = StringIO()
        set_appearance_state(stream, A)
        stream.write('{} {} m '.format(points[0][0], points[0][1]))
        for x, y in points[1:]:
            stream.write('{} {} l '.format(x, y))
        stream.write('h ')
        stroke_or_fill(stream, A)

        return stream.getvalue()

    def as_pdf_object(self):
        obj = self.base_points_object()
        if self._appearance.fill:
            obj.IC = self._appearance.fill
        obj.Vertices = flatten_points(self._location.points)
        return obj


class Polyline(PointsAnnotation):
    subtype = 'PolyLine'
    versions = ('1.5', '1.6', '1.7')

    def graphics_commands(self):
        A = self._appearance
        points = self._location.points

        stream = StringIO()
        set_appearance_state(stream, A)
        stream.write('{} {} m '.format(points[0][0], points[0][1]))
        for x, y in points[1:]:
            stream.write('{} {} l '.format(x, y))
        # TODO add a 'close' attribute?
        stroke(stream)

        return stream.getvalue()

    def as_pdf_object(self):
        obj = self.base_points_object()
        if self._appearance.fill:
            obj.IC = self._appearance.fill
        obj.Vertices = flatten_points(self._location.points)
        return obj


class Ink(PointsAnnotation):
    subtype = 'Ink'

    def graphics_commands(self):
        A = self._appearance
        points = self._location.points

        stream = StringIO()
        set_appearance_state(stream, A)
        stream.write('{} {} m '.format(points[0][0], points[0][1]))
        # TODO "real" PDF editors do smart smoothing of ink points using
        # interpolated Bezier curves.
        for x, y in points[1:]:
            stream.write('{} {} l '.format(x, y))
        stroke(stream)

        return stream.getvalue()

    def as_pdf_object(self):
        obj = self.base_points_object()
        obj.InkList = [flatten_points(self._location.points)]
        return obj
