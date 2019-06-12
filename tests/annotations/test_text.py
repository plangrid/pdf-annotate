# -*- coding: utf-8 -*-
import sys

from unittest import TestCase

from pdf_annotate.annotations.text import FreeText
from pdf_annotate.config.appearance import Appearance
from pdf_annotate.config.constants import PDF_ANNOTATOR_FONT
from pdf_annotate.config.location import Location
from pdf_annotate.util.geometry import identity
from pdf_annotate.util.geometry import translate


class TestText(TestCase):

    def test_pdf_object(self):
        x1, y1, x2, y2 = 10, 20, 100, 200
        annotation = FreeText(
            Location(x1=x1, y1=y1, x2=x2, y2=y2, page=0),
            Appearance(
                fill=[0.4, 0, 0],
                stroke_width=1,
                font_size=5,
                content='Hi',
            ),
        )
        obj = annotation.as_pdf_object(identity(), page=None)
        assert obj.AP.N.stream == (
            'q BT 0.4 0 0 rg /{} 5 Tf '
            '1 0 0 1 11 109 Tm (Hi) Tj ET Q'
        ).format(PDF_ANNOTATOR_FONT)
        assert obj.DA == '0.4 0 0 rg /{} 5 Tf'.format(PDF_ANNOTATOR_FONT)
        assert obj.Rect == [x1, y1, x2, y2]
        assert obj.AP.N.BBox == [x1, y1, x2, y2]
        assert obj.AP.N.Matrix == translate(-x1, -y1)

    def test_unicode_content(self):
        # Python2.7 chokes on the string validation because we're passing in a unicode string
        # But this functionality shouldn't be being used currently
        if sys.version_info.major >= 3:
            x1, y1, x2, y2 = 10, 20, 100, 200
            annotation = FreeText(
                Location(x1=x1, y1=y1, x2=x2, y2=y2, page=0),
                Appearance(
                    fill=[0.4, 0, 0],
                    stroke_width=1,
                    font_size=5,
                    content=u'Hello World\u2757',
                ),
            )
            obj = annotation.as_pdf_object(identity(), page=None)
            assert obj.AP.N.stream == (
                'q BT 0.4 0 0 rg /{} 5 Tf '
                '1 0 0 1 11 109 Tm <FEFF00480065006C006C006F00200057006F0072006C00642757> Tj ET Q'
            ).format(PDF_ANNOTATOR_FONT)

    def test_octal_content(self):
        x1, y1, x2, y2 = 10, 20, 100, 200
        annotation = FreeText(
            Location(x1=x1, y1=y1, x2=x2, y2=y2, page=0),
            Appearance(
                fill=[0.4, 0, 0],
                stroke_width=1,
                font_size=5,
                content='Hiα',
            ),
        )
        obj = annotation.as_pdf_object(identity(), page=None)
        if sys.version_info.major < 3:
            assert obj.AP.N.stream == (
                'q BT 0.4 0 0 rg /{} 5 Tf '
                '1 0 0 1 11 109 Tm (Hi\xce\xb1) Tj ET Q'
            ).format(PDF_ANNOTATOR_FONT)
        else:
            assert obj.AP.N.stream == (
                'q BT 0.4 0 0 rg /{} 5 Tf '
                '1 0 0 1 11 109 Tm <FEFF0048006903B1> Tj ET Q'
            ).format(PDF_ANNOTATOR_FONT)
