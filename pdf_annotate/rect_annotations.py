import warnings

from six import StringIO

from pdf_annotate.annotations import Annotation
from pdf_annotate.annotations import make_border_dict
from pdf_annotate.graphics import set_appearance_state
from pdf_annotate.graphics import stroke_or_fill
from pdf_annotate.location import Location
from pdf_annotate.utils import translate


class RectAnnotation(Annotation):
    """Abstract annotation that defines its location on the document with a
    width and a height.
    """
    @staticmethod
    def rotate(location, rotate, page_size):
        if rotate == 0:
            return location

        l = location.copy()
        if rotate == 90:
            width = page_size[1]
            l.x1 = width - location.y2
            l.y1 = location.x1
            l.x2 = width - location.y1
            l.y2 = location.x2
        elif rotate == 180:
            width, height = page_size
            l.x1 = width - location.x2
            l.y1 = height - location.y2
            l.x2 = width - location.x1
            l.y2 = height - location.y1
        elif rotate == 270:
            height = page_size[0]
            l.x1 = location.y1
            l.y1 = height - location.x2
            l.x2 = location.y2
            l.y2 = height - location.x1

        l.rotation = rotate

        return l

    @staticmethod
    def scale(location, scale):
        x_scale, y_scale = scale
        l = location.copy()
        l.x1 = location.x1 * x_scale
        l.y1 = location.y1 * y_scale
        l.x2 = location.x2 * x_scale
        l.y2 = location.y2 * y_scale
        return l

    def get_matrix(self):
        stroke_width = self._appearance.stroke_width
        L = self._location
        return translate(-(L.x1 - stroke_width), -(L.y1 - stroke_width))

    def make_rect(self):
        stroke_width = self._appearance.stroke_width
        L = self._location
        return [
            L.x1 - stroke_width,
            L.y1 - stroke_width,
            L.x2 + stroke_width,
            L.y2 + stroke_width,
        ]

    def as_pdf_object(self):
        obj = self.make_base_object()
        A = self._appearance
        obj.BS = make_border_dict(A)
        obj.C = A.stroke_color
        if A.fill:
            obj.IC = A.fill
        obj.AP = self.make_ap_dict()
        padding = A.stroke_width / 2.0
        obj.RD = [padding, padding, padding, padding]
        return obj


class Square(RectAnnotation):
    subtype = 'Square'

    def graphics_commands(self):
        L = self._location
        A = self._appearance
        stream = StringIO()

        set_appearance_state(stream, A)
        stream.write('{} {} {} {} re '.format(
            L.x1,
            L.y1,
            L.x2 - L.x1,
            L.y2 - L.y1,
        ))
        stroke_or_fill(stream, A)

        # TODO dash array
        return stream.getvalue()


class Circle(RectAnnotation):
    """Circles and Squares are basically the same PDF annotation but with
    different content streams.
    """
    subtype = 'Circle'

    def graphics_commands(self):
        L = self._location
        A = self._appearance

        # PDF graphics operators doesn't have an ellipse method, so we have to
        # construct it from four bezier curves
        left_x = L.x1
        right_x = L.x2
        bottom_x = left_x + (right_x - left_x) / 2.0
        top_x = bottom_x

        bottom_y = L.y1
        top_y = L.y2
        left_y = bottom_y + (top_y - bottom_y) / 2.0
        right_y = left_y

        stream = StringIO()
        set_appearance_state(stream, A)
        # Move to the bottom of the circle, then four curves around.
        # https://stackoverflow.com/questions/1734745/how-to-create-circle-with-b%C3%A9zier-curves
        cp_offset = 0.552284749831
        stream.write('{} {} m '.format(bottom_x, bottom_y))
        stream.write('{} {} {} {} {} {} c '.format(
            bottom_x + (right_x - bottom_x) * cp_offset, bottom_y,
            right_x, right_y - (right_y - bottom_y) * cp_offset,
            right_x, right_y,
        ))
        stream.write('{} {} {} {} {} {} c '.format(
            right_x, right_y + (top_y - right_y) * cp_offset,
            top_x + (right_x - top_x) * cp_offset, top_y,
            top_x, top_y,
        ))
        stream.write('{} {} {} {} {} {} c '.format(
            top_x - (top_x - left_x) * cp_offset, top_y,
            left_x, left_y + (top_y - left_y) * cp_offset,
            left_x, left_y,
        ))
        stream.write('{} {} {} {} {} {} c '.format(
            left_x, left_y - (left_y - bottom_y) * cp_offset,
            bottom_x - (bottom_x - left_x) * cp_offset, bottom_y,
            bottom_x, bottom_y,
        ))
        stream.write('h ')
        stroke_or_fill(stream, A)

        return stream.getvalue()
