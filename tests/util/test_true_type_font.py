from unittest import mock
from unittest import TestCase

from pdf_annotate.annotations.text import HELVETICA_PATH
from pdf_annotate.config.constants import DEFAULT_BASE_FONT
from pdf_annotate.util.true_type_font import get_true_type_font
from pdf_annotate.util.true_type_font import TrueTypeFont


class TestTrueTypeFont(TestCase):

    @classmethod
    def setUpClass(self):
        self.font_size = 16
        self.font = TrueTypeFont(
            path=HELVETICA_PATH,
            font_name=DEFAULT_BASE_FONT,
            font_size=self.font_size,
        )

    def test_measure_text(self):
        # Sanity check measuring simple text
        assert round(self.font.measure_text('abc', 16)) == 26
        assert round(self.font.measure_text('abc', 20)) == 32

    def test_measure_missing_chars_equal_width(self):
        # The default font shouldn't have this (U+5076)
        char_a = 'Ꮤ'
        # This is the widest unicode character, supposedly: U+65021
        char_b = '﷽'
        # They should both measure as notdef, so have equal width
        width_a = self.font.measure_text(char_a)
        width_b = self.font.measure_text(char_b)
        assert width_a == width_b

    def test_composability(self):
        missing_char = 'Ꮤ'
        text = 'Hi there, missing char is: '
        assert self.font.measure_text(text + missing_char) == (
            (
                self.font.measure_text(text) +
                self.font.measure_text(missing_char)
            )
        )

    def test_missing_font_size(self):
        font = TrueTypeFont(HELVETICA_PATH, DEFAULT_BASE_FONT)
        with self.assertRaises(ValueError):
            font.measure_text('hi')

    def test_font_cache(self):
        get_true_type_font(HELVETICA_PATH, DEFAULT_BASE_FONT)
        with mock.patch('pdf_annotate.util.true_type_font.TrueTypeFont') as mock_get:
            get_true_type_font(HELVETICA_PATH, DEFAULT_BASE_FONT)

        assert not mock_get.called

        # Using different params means you skip the cache
        with mock.patch('pdf_annotate.util.true_type_font.TrueTypeFont') as mock_get:
            get_true_type_font(HELVETICA_PATH, DEFAULT_BASE_FONT, 16)

        assert mock_get.called
