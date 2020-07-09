# -*- coding: utf-8 -*-
"""
    Points annotations
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    Annotations that are defined by a series of points: Line, Polygon, Polyline

    :copyright: Copyright 2019 Autodesk, Inc.
    :license: MIT, see LICENSE for details.
"""
from pdf_annotate.annotations.base import Annotation
from pdf_annotate.annotations.base import make_border_dict
from pdf_annotate.config.appearance import set_appearance_state
from pdf_annotate.config.appearance import stroke_or_fill
from pdf_annotate.graphics import Close
from pdf_annotate.graphics import ContentStream
from pdf_annotate.graphics import Line as CSLine
from pdf_annotate.graphics import Move
from pdf_annotate.graphics import Restore
from pdf_annotate.graphics import Save
from pdf_annotate.graphics import Stroke


def flatten_points(points):
    return [v for point in points for v in point]


class PointsAnnotation(Annotation):
    """An abstract annotation that defines its location on the document with
    an array of points.
    """

    def make_rect(self):
        L = self._location
        stroke_width = self._appearance.stroke_width
        p = L.points[0]
        min_x, max_x, min_y, max_y = p[0], p[0], p[1], p[1]
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

    def base_points_object(self):
        obj = self.make_base_object()
        obj.BS = make_border_dict(self._appearance)
        obj.C = self._appearance.stroke_color
        # TODO line endings, leader lines, captions
        return obj


class Line(PointsAnnotation):
    subtype = 'Line'

    def make_appearance_stream(self):
        A = self._appearance
        points = self._location.points

        stream = ContentStream([Save()])
        set_appearance_state(stream, A)
        stream.add(Move(points[0][0], points[0][1]))
        stream.add(CSLine(points[1][0], points[1][1]))
        stroke_or_fill(stream, A)
        stream.add(Restore())

        return stream

    def add_additional_pdf_object_data(self, obj):
        # TODO line endings, leader lines, captions
        obj.L = flatten_points(self._location.points)


class Polygon(PointsAnnotation):
    subtype = 'Polygon'
    versions = ('1.5', '1.6', '1.7')

    def make_appearance_stream(self):
        A = self._appearance
        points = self._location.points

        stream = ContentStream([Save()])
        set_appearance_state(stream, A)
        stream.add(Move(points[0][0], points[0][1]))
        for x, y in points[1:]:
            stream.add(CSLine(x, y))
        stream.add(Close())
        stroke_or_fill(stream, A)
        stream.add(Restore())

        return stream

    def add_additional_pdf_object_data(self, obj):
        if self._appearance.fill:
            obj.IC = self._appearance.fill
        obj.Vertices = flatten_points(self._location.points)


class Polyline(PointsAnnotation):
    subtype = 'PolyLine'
    versions = ('1.5', '1.6', '1.7')

    def make_appearance_stream(self):
        A = self._appearance
        points = self._location.points

        stream = ContentStream([Save()])
        set_appearance_state(stream, A)
        stream.add(Move(points[0][0], points[0][1]))
        for x, y in points[1:]:
            stream.add(CSLine(x, y))
        # TODO add a 'close' attribute?
        stream.extend([Stroke(), Restore()])

        return stream

    def add_additional_pdf_object_data(self, obj):
        obj.Vertices = flatten_points(self._location.points)


class Ink(PointsAnnotation):
    subtype = 'Ink'

    def make_appearance_stream(self):
        A = self._appearance
        points = self._location.points

        stream = ContentStream([Save()])
        set_appearance_state(stream, A)
        stream.add(Move(points[0][0], points[0][1]))
        # TODO "real" PDF editors do smart smoothing of ink points using
        # interpolated Bezier curves.
        for x, y in points[1:]:
            stream.add(CSLine(x, y))
        stream.extend([Stroke(), Restore()])

        return stream

    def add_additional_pdf_object_data(self, obj):
        obj.InkList = [flatten_points(self._location.points)]
