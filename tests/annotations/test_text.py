from unittest import TestCase

from pdf_annotate.annotations.text import FreeText, NoteText, HELVETICA_PATH
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


    def test_text_note_pdf_object(self):
        x1, y1, x2, y2 = 10, 20, 100, 200
        annotation = NoteText(
            Location(x1=x1, y1=y1, x2=x2, y2=y2, page=0),
            Appearance(
                fill=[0.4, 0, 0],
                content='Hi',
                text_name='Comment',
            ),
        )
        obj = annotation.as_pdf_object(identity(), page=None)
        assert obj.Rect == [x1, y1, x2, y2]
        assert obj.C == [0.4, 0, 0]
        assert obj.Name == '/Comment'
        assert obj.Contents == 'Hi'


    def test_make_composite_font(self):
        font = FreeText.make_composite_font_object(HELVETICA_PATH)
        keys = font.keys()
        expected_keys = ['/Type', '/Subtype', '/BaseFont', '/Encoding', '/DescendantFonts', '/ToUnicode']
        assert all(key in keys for key in expected_keys)
        assert font['/Type'] == '/Font'
        assert font['/Subtype'] == '/Type0'
        assert len(font['/DescendantFonts']) == 1
        descendant_font = font['/DescendantFonts'][0]
        assert descendant_font['/Type'] == '/Font'
        assert descendant_font['/Subtype'] == '/CIDFontType2'
        assert descendant_font['/BaseFont'] == font['/BaseFont']
