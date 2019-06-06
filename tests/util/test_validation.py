# -*- coding: utf-8 -*-
from unittest import TestCase

import attr
import pytest

from pdf_annotate.config.constants import BLACK
from pdf_annotate.graphics import ContentStream
from pdf_annotate.util.validation import between
from pdf_annotate.util.validation import Boolean
from pdf_annotate.util.validation import Color
from pdf_annotate.util.validation import Enum
from pdf_annotate.util.validation import Field
from pdf_annotate.util.validation import Integer
from pdf_annotate.util.validation import Number
from pdf_annotate.util.validation import Points
from pdf_annotate.util.validation import positive
from pdf_annotate.util.validation import String


GRAY = [0, 0, 0, 0.5]
VALUES = (1, 2, 3)


class TestRequired(TestCase):
    """Specifying attributes without defaults means they're required."""
    @attr.s
    class R(object):
        b = Boolean()
        e = Enum(VALUES)

    def test_required(self):
        with pytest.raises(TypeError):
            self.R()
            self.R(b=False)
        assert self.R(b=False, e=1)


class TestBoolean(TestCase):
    @attr.s
    class B(object):
        b = Boolean(default=False)

    def test_boolean(self):
        assert self.B(True).b
        assert not self.B().b


class TestColor(TestCase):
    @attr.s
    class C(object):
        c = Color(default=BLACK)

    def test_color(self):
        assert self.C().c == BLACK
        assert self.C([1, 1, 1]).c == [1, 1, 1]

    def test_transparent(self):
        assert self.C(GRAY).c == GRAY

    def test_invalid_colors(self):
        with pytest.raises(ValueError):
            self.C(['a', 1, 1])
        with pytest.raises(ValueError):
            self.C([1, 1])
        with pytest.raises(ValueError):
            self.C('black')


class TestEnum(TestCase):
    @attr.s
    class E(object):
        e = Enum(VALUES, default=2)

    def test_enum(self):
        assert self.E().e == 2

    def test_not_in_enum(self):
        with pytest.raises(ValueError):
            self.E(54)


def validate_custom_field(obj, attr, value):
    if isinstance(value, dict) and len(value) != 2:
        raise ValueError('Value must be length 6')


class TestField(TestCase):

    @attr.s
    class F(object):
        integer = Field(int, default=None)
        content_stream = Field(ContentStream, default=None)
        custom = Field(dict, default=None, validator=validate_custom_field)

    def test_disallowed_type(self):
        with pytest.raises(ValueError):
            self.F(integer='string')

    def test_field(self):
        content_stream = ContentStream([])
        f = self.F(integer=2, content_stream=content_stream)
        assert f.integer == 2
        assert f.content_stream is content_stream

    def test_custom_validator(self):
        with pytest.raises(ValueError):
            self.F(custom={})
        d = {'a': 1, 'b': 2}
        assert self.F(custom=d).custom == d


class TestInteger(TestCase):

    @attr.s
    class Int(object):
        i = Integer(default=None)
        positive = Integer(default=1, validator=positive)

    def test_integer(self):
        assert self.Int().i is None
        assert self.Int(12).i == 12

    def test_positive(self):
        with pytest.raises(ValueError):
            self.Int(positive=-1)
        assert self.Int(positive=2).positive == 2

    def test_invalid_integer(self):
        with pytest.raises(ValueError):
            self.Int('abc')


class TestNumber(TestCase):

    @attr.s
    class N(object):
        default = Number(default=1.5)
        positive = Number(default=None, validator=positive)
        between = Number(default=None, validator=between(0, 1))

    def test_positive(self):
        with pytest.raises(ValueError):
            self.N(positive=-15)
        assert self.N(positive=15).positive == 15

    def test_between(self):
        with pytest.raises(ValueError):
            self.N(between=-1)
        assert self.N(between=0.5).between == 0.5

    def test_default(self):
        assert self.N().default == 1.5


class TestPoints(TestCase):

    @attr.s
    class P(object):
        p = Points(default=None)

    def test_points(self):
        points = [[1, 1], [1.5, 1.5]]
        assert self.P(points).p == points

    def test_not_points(self):
        with pytest.raises(ValueError):
            self.P([[1, 'a']])
        with pytest.raises(ValueError):
            self.P('points')


class TestString(TestCase):

    @attr.s
    class S(object):
        s = String(default='s')

    def test_string(self):
        assert self.S().s == 's'
        assert self.S('string').s == 'string'

    def test_not_string(self):
        with pytest.raises(ValueError):
            self.S(12)
