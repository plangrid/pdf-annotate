from unittest import TestCase

from pdf_annotate.annotations.rect import Circle
from pdf_annotate.annotations.rect import Square
from pdf_annotate.config.appearance import Appearance
from pdf_annotate.config.location import Location
from pdf_annotate.util.geometry import identity
from pdf_annotate.util.geometry import translate


class TestSquare(TestCase):

    def test_pdf_object(self):
        x1, y1, x2, y2 = 10, 20, 100, 200
        annotation = Square(
            Location(x1=x1, y1=y1, x2=x2, y2=y2, page=0),
            Appearance(stroke_width=1),
        )
        obj = annotation.as_pdf_object(identity(), page=None)
        assert obj.AP.N.stream == 'q 0 0 0 RG 1 w 10 20 90 180 re S Q'
        padded_rect = [x1 - 1, y1 - 1, x2 + 1, y2 + 1]
        assert obj.Rect == padded_rect
        assert obj.AP.N.BBox == padded_rect
        assert obj.AP.N.Matrix == translate(-(x1 - 1), -(y1 - 1))


class TestCircle(TestCase):

    def test_pdf_object(self):
        x1, y1, x2, y2 = 10, 20, 100, 200
        annotation = Circle(
            Location(x1=x1, y1=y1, x2=x2, y2=y2, page=0),
            Appearance(stroke_width=1),
        )
        obj = annotation.as_pdf_object(identity(), page=None)
        # Circles have these complicated Bezier curve streams, so don't bother
        # checking it in the unit test.
        padded_rect = [x1 - 1, y1 - 1, x2 + 1, y2 + 1]
        assert obj.Rect == padded_rect
        assert obj.AP.N.BBox == padded_rect
        assert obj.AP.N.Matrix == translate(-(x1 - 1), -(y1 - 1))
