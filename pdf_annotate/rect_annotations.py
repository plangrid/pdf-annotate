# -*- coding: utf-8 -*-
"""
Square and Circle annotations.
"""
import warnings

from pdf_annotate.annotations import Annotation
from pdf_annotate.annotations import make_border_dict
from pdf_annotate.graphics import ContentStream, Rect, Stroke, Bezier, Close, Move
from pdf_annotate.graphics import set_appearance_state
from pdf_annotate.graphics import stroke_or_fill
from pdf_annotate.location import Location
from pdf_annotate.utils import translate
from pdf_annotate.utils import transform_point


class RectAnnotation(Annotation):
    """Abstract annotation that defines its location on the document with a
    width and a height.
    """
    @staticmethod
    def transform(location, transform):
        l = location.copy()

        x1, y1 = transform_point([l.x1, l.y1], transform)
        x2, y2 = transform_point([l.x2, l.y2], transform)
        l.x1, l.x2 = sorted([x1, x2])
        l.y1, l.y2 = sorted([y1, y2])

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
        padding = A.stroke_width / 2.0
        obj.RD = [padding, padding, padding, padding]
        return obj


class Square(RectAnnotation):
    subtype = 'Square'

    def graphics_commands(self):
        L = self._location
        A = self._appearance
        stream = ContentStream()

        set_appearance_state(stream, A)
        stream.add(Rect(
            L.x1,
            L.y1,
            L.x2 - L.x1,
            L.y2 - L.y1,
        ))
        stroke_or_fill(stream, A)

        # TODO dash array
        return stream.resolve()


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

        stream = ContentStream()
        set_appearance_state(stream, A)
        # Move to the bottom of the circle, then four curves around.
        # https://stackoverflow.com/questions/1734745/how-to-create-circle-with-b%C3%A9zier-curves
        cp_offset = 0.552284749831
        stream.add(Move(bottom_x, bottom_y))
        stream.add(Bezier(
            bottom_x + (right_x - bottom_x) * cp_offset, bottom_y,
            right_x, right_y - (right_y - bottom_y) * cp_offset,
            right_x, right_y,
        ))
        stream.add(Bezier(
            right_x, right_y + (top_y - right_y) * cp_offset,
            top_x + (right_x - top_x) * cp_offset, top_y,
            top_x, top_y,
        ))
        stream.add(Bezier(
            top_x - (top_x - left_x) * cp_offset, top_y,
            left_x, left_y + (top_y - left_y) * cp_offset,
            left_x, left_y,
        ))
        stream.add(Bezier(
            left_x, left_y - (left_y - bottom_y) * cp_offset,
            bottom_x - (bottom_x - left_x) * cp_offset, bottom_y,
            bottom_x, bottom_y,
        ))
        stream.add(Close())
        stroke_or_fill(stream, A)

        return stream.resolve()
