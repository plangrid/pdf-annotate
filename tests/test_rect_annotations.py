from unittest import TestCase

from pdf_annotate.appearance import Appearance
from pdf_annotate.location import Location
from pdf_annotate.rect_annotations import Circle
from pdf_annotate.rect_annotations import RectAnnotation
from pdf_annotate.rect_annotations import Square


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

    def test_no_rotate(self):
        location = RectAnnotation.rotate(self.L, 0, (self.width, self.height))
        self.assertDimensions(location, [10, 20, 30, 30])

    def test_rotate_90(self):
        location = RectAnnotation.rotate(self.L, 90, (self.height, self.width))
        self.assertDimensions(location, [70, 10, 80, 30])

    def test_rotate_180(self):
        location = RectAnnotation.rotate(self.L, 180, (self.width, self.height))
        self.assertDimensions(location, [70, 170, 90, 180])

    def test_rotate_270(self):
        location = RectAnnotation.rotate(self.L, 270, (self.height, self.width))
        self.assertDimensions(location, [20, 170, 30, 190])

    def test_scale(self):
        location = RectAnnotation.scale(self.L, (2, 2))
        self.assertDimensions(location, [20, 40, 60, 60])

    def test_scale_x_y(self):
        location = RectAnnotation.scale(self.L, (2, 3))
        self.assertDimensions(location, [20, 60, 60, 90])


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
            '/F': 4,
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
            '/F': 4,
            '/RD': [0.5, 0.5, 0.5, 0.5],
            '/Rect': [9, 9, 21, 21],
            '/Subtype': '/Circle',
            '/Type': '/Annot',
        }
        d = dict(obj)
        d['/AP']['/N'].pop('/Length')
        assert d == expected_dict
