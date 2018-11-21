# -*- coding: utf-8 -*-
from unittest import TestCase

from pdf_annotate.util.text import get_wrapped_lines
from pdf_annotate.util.text import unshift_line
from pdf_annotate.util.text import unshift_token


class TestUnshiftToken(TestCase):

    def test_empty_token(self):
        assert unshift_token('') == {
            'text': '',
            'separator': '',
            'remainder': '',
        }

    def test_newline_token(self):
        assert unshift_token('\n') == {
            'text': '',
            'separator': '\n',
            'remainder': '',
        }

    def test_spaces_token(self):
        assert unshift_token('   ') == {
            'text': '   ',
            'separator': '',
            'remainder': '',
        }

    def test_abc_token(self):
        assert unshift_token('ABC') == {
            'text': 'ABC',
            'separator': '',
            'remainder': '',
        }

    def test_abc_space_token(self):
        assert unshift_token('ABC ') == {
            'text': 'ABC',
            'separator': ' ',
            'remainder': '',
        }

    def test_space_a_token(self):
        assert unshift_token(' A') == {
            'text': ' ',
            'separator': '',
            'remainder': 'A',
        }

    def test_abc_newline_token(self):
        assert unshift_token('ABC\n') == {
            'text': 'ABC',
            'separator': '\n',
            'remainder': '',
        }

    def test_abc_newline_a_token(self):
        assert unshift_token('ABC\nA') == {
            'text': 'ABC',
            'separator': '\n',
            'remainder': 'A',
        }


class TestUnshiftLine(TestCase):

    @staticmethod
    def measure(text):
        return len(text)

    def test_break_midword_length_0(self):
        assert unshift_line('test', self.measure, 0) == {
            'text': 't',
            'remainder': 'est',
        }

    def test_single_character_length_0(self):
        assert unshift_line('t', self.measure, 0) == {
            'text': 't',
            'remainder': '',
        }

    def test_newline(self):
        assert unshift_line('\n', self.measure, 10) == {
            'text': '',
            'remainder': '',
        }

    def test_trailing_newline(self):
        assert unshift_line('test\n', self.measure, 10) == {
            'text': 'test',
            'remainder': '',
        }

    def test_break_between_words(self):
        assert unshift_line('test\nabc', self.measure, 10) == {
            'text': 'test',
            'remainder': 'abc',
        }
        assert unshift_line('123\n567890', self.measure, 6) == {
            'text': '123',
            'remainder': '567890',
        }

    def test_break_midword(self):
        assert unshift_line('123456789', self.measure, 8) == {
            'text': '12345678',
            'remainder': '9',
        }

    def test_prefer_space_breaks(self):

        assert unshift_line('123 56789', self.measure, 6) == {
            'text': '123 ',
            'remainder': '56789',
        }
        assert unshift_line('123 56 890', self.measure, 6) == {
            'text': '123 56 ',
            'remainder': '890',
        }


class TestGetWrappedLines(TestCase):

    def test_wrap_lines(self):
        lines = get_wrapped_lines(
            "Hi, I'm a big block of text!",
            lambda text: len(text),
            10,
        )
        assert lines == [
            "Hi, I'm a ",
            "big block ",
            "of text!",
        ]

    def test_single_line(self):
        lines = get_wrapped_lines('Hi', lambda text: len(text), 10)
        assert lines == ['Hi']
