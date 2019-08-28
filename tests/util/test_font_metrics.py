from unittest import TestCase
from unittest.mock import MagicMock, PropertyMock

from pdf_annotate.util.true_type_font import TrueTypeFont


class TestFontMetrics(TestCase):
    def test__format_widths_empty(self):
        widths = TrueTypeFont._format_widths({}, {}, [])
        assert widths == []

    def test__format_widths_single(self):
        cmap = {
            15: 0,
        }
        glyph = MagicMock()
        p = PropertyMock(return_value=250)
        type(glyph).width = p
        glyph_set = [glyph]
        cids = [15]
        widths = TrueTypeFont._format_widths(glyph_set, cmap, cids)
        assert p.call_count == 1
        assert widths == [15, 15, 250]

    def test__format_widths_constant_segment(self):
        cmap = {
            15: 0,
            16: 1,
            17: 2,
        }
        glyph = MagicMock()
        p = PropertyMock(return_value=250)
        type(glyph).width = p
        glyph_set = [glyph, glyph, glyph]
        cids = [15, 16, 17]
        widths = TrueTypeFont._format_widths(glyph_set, cmap, cids)
        assert p.call_count == 3
        assert widths == [15, 17, 250]

    def test__format_widths_both(self):
        cmap = {
            15: 0,
            16: 0,
            17: 0,
            19: 1,
            20: 1,
            22: 2,
            23: 1,
            24: 0,
        }
        glyph = MagicMock()
        p = PropertyMock(return_value=400)
        type(glyph).width = p
        glyph2 = MagicMock()
        p2 = PropertyMock(return_value=800)
        type(glyph2).width = p2
        glyph3 = MagicMock()
        p3 = PropertyMock(return_value=600)
        type(glyph3).width = p3
        glyph_set = [glyph, glyph2, glyph3]
        cids = [15, 16, 17, 19, 20, 22, 23, 24]
        widths = TrueTypeFont._format_widths(glyph_set, cmap, cids)
        assert p.call_count == 4
        assert p2.call_count == 3
        assert p3.call_count == 1
        assert widths == [15, 17, 400, 19, 20, 800, 22, [600, 800, 400]]
