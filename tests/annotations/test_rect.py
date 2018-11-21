from unittest import TestCase

from pdf_annotate.annotations.rect import Circle
from pdf_annotate.annotations.rect import RectAnnotation
from pdf_annotate.annotations.rect import Square
from pdf_annotate.config.appearance import Appearance
from pdf_annotate.config.location import Location
from pdf_annotate.graphics import Close
from pdf_annotate.graphics import ContentStream
from pdf_annotate.graphics import Line
from pdf_annotate.graphics import Move
from pdf_annotate.util.geometry import scale
from tests.annotations import ANNOTATORS


class TestRectAnnotation(TestCase):

    def setUp(self):
        self.A = Appearance(stroke_width=1)
        self.L = Location(x1=10, y1=20, x2=30, y2=30, page=0)
        self.width = 100
        self.height = 200

    def assertDimensions(self, location, dimensions):
        x1, y1, x2, y2 = dimensions
        assert location.x1 == x1
        assert location.y1 == y1
        assert location.x2 == x2
        assert location.y2 == y2

    def test_transform(self):
        location = RectAnnotation.transform(self.L, scale(2, 3))
        self.assertDimensions(location, [20, 60, 60, 90])

    def test_custom_appearance_stream(self):
        stream = ContentStream([
            Move(0, 0),
            Line(10, 10),
            Line(20, 20),
            Close(),
        ])
        A = Appearance(stroke_width=1, appearance_stream=stream)
        L = Location(x1=10, y1=10, x2=20, y2=20, page=0)
        annotation = ANNOTATORS['simple'].get_annotation('square', L, A, None)
        obj = annotation.as_pdf_object()
        # TODO almost works
        assert obj.AP.N.stream == '0 0 m 10 10 l 20 20 l h'


class TestSquare(TestCase):

    def test_pdf_object(self):
        # Big ugly hammer of a test to test PDF object creation end to end
        A = Appearance(stroke_width=1)
        L = Location(x1=10, y1=10, x2=20, y2=20, page=0)
        annotation = Square(L, A)
        obj = annotation.as_pdf_object()
        expected_dict = {
            '/AP': {
                '/N': {
                    '/BBox': [9, 9, 21, 21],
                    '/FormType': 1,
                    '/Matrix': [1, 0, 0, 1, -9, -9],
                    '/Resources': {'/ProcSet': '/PDF'},
                    '/Subtype': '/Form',
                    '/Type': '/XObject'
                }
            },
            '/BS': {'/S': '/S', '/Type': '/Border', '/W': 1},
            '/C': (0, 0, 0),
            '/RD': [0.5, 0.5, 0.5, 0.5],
            '/Rect': [9, 9, 21, 21],
            '/Subtype': '/Square',
            '/Type': '/Annot',
        }
        d = dict(obj)
        d['/AP']['/N'].pop('/Length')
        assert d == expected_dict


class TestCircle(TestCase):

    def test_pdf_object(self):
        # Big ugly hammer of a test to test PDF object creation end to end
        A = Appearance(stroke_width=1)
        L = Location(x1=10, y1=10, x2=20, y2=20, page=0)
        annotation = Circle(L, A)
        obj = annotation.as_pdf_object()
        expected_dict = {
            '/AP': {
                '/N': {
                    '/BBox': [9, 9, 21, 21],
                    '/FormType': 1,
                    '/Matrix': [1, 0, 0, 1, -9, -9],
                    '/Resources': {'/ProcSet': '/PDF'},
                    '/Subtype': '/Form',
                    '/Type': '/XObject'
                }
            },
            '/BS': {'/S': '/S', '/Type': '/Border', '/W': 1},
            '/C': (0, 0, 0),
            '/RD': [0.5, 0.5, 0.5, 0.5],
            '/Rect': [9, 9, 21, 21],
            '/Subtype': '/Circle',
            '/Type': '/Annot',
        }
        d = dict(obj)
        d['/AP']['/N'].pop('/Length')
        assert d == expected_dict
