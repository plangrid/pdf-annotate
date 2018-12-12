from unittest import TestCase

from pdf_annotate.annotations.text import FreeText
from pdf_annotate.config.appearance import Appearance
from pdf_annotate.config.location import Location
from pdf_annotate.util.geometry import identity
from pdf_annotate.util.geometry import translate


class TestText(TestCase):

    def test_pdf_object(self):
        x1, y1, x2, y2 = 10, 20, 100, 200
        annotation = FreeText(
            Location(x1=x1, y1=y1, x2=x2, y2=y2, page=0),
            Appearance(stroke_width=1, font_size=5, content='Hi'),
        )
        obj = annotation.as_pdf_object(identity(), page=None)
        assert obj.AP.N.stream == (
            'q 1 1 1 RG 0 0 0 rg 0 w BT 0 0 0 RG /PDFANNOTATORFONT1 5 Tf '
            '1 0 0 1 11 109 Tm (Hi) Tj ET Q'
        )
        assert obj.Rect == [x1, y1, x2, y2]
        assert obj.AP.N.BBox == [x1, y1, x2, y2]
        assert obj.AP.N.Matrix == translate(-x1, -y1)
