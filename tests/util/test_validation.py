# -*- coding: utf-8 -*-
from unittest import TestCase

import attr
import nose

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

    @attr.s
    class R(object):
        b = Boolean(required=True)
        c = Color(required=True)
        e = Enum(VALUES, required=True)
        f = Field(int, required=True)
        i = Integer(required=True)
        n = Number(required=True)
        p = Points(required=True)
        s = String(required=True)

    def test_required(self):
        kwargs = {}
        values = [
            ('b', False),
            ('c', BLACK),
            ('e', 1),
            ('f', 15),
            ('i', 2),
            ('n', 0.5),
            ('p', [[1, 1], [2, 2]]),
            ('s', 'something'),
        ]
        for key, value in values:
            with nose.tools.assert_raises(TypeError):
                self.R(**kwargs)
            kwargs[key] = value

        assert self.R(**kwargs)


class TestBoolean(TestCase):
    @attr.s
    class B(object):
        boolean = Boolean()
        default_false = Boolean(False)

    def test_boolean(self):
        b = self.B(boolean=True)
        assert b.boolean
        assert not b.default_false


class TestColor(TestCase):
    @attr.s
    class C(object):
        default = Color()
        not_none = Color(BLACK, allow_none=False)

    def test_color(self):
        c = self.C(not_none=BLACK)
        assert c.default is None
        assert c.not_none == BLACK

    def test_transparent(self):
        c = self.C(default=GRAY)
        assert c.default == GRAY

    def test_not_none(self):
        with nose.tools.assert_raises(ValueError):
            self.C(not_none=None)


class TestEnum(TestCase):

    @attr.s
    class E(object):
        default = Enum(VALUES)

    def test_enum(self):
        e = self.E(default=2)
        assert e.default == 2

    def test_not_in_enum(self):
        with nose.tools.assert_raises(ValueError):
            self.E(default=54)

    def test_none(self):
        e = self.E()
        assert e.default is None


class TestField(TestCase):

    @attr.s
    class F(object):
        integer = Field(int)
        content_stream = Field(ContentStream)

    def test_disallowed_type(self):
        with nose.tools.assert_raises(ValueError):
            self.F(integer='string')

    def test_field(self):
        content_stream = ContentStream([])
        f = self.F(integer=2, content_stream=content_stream)
        assert f.integer == 2
        assert f.content_stream is content_stream


class TestInteger(TestCase):

    @attr.s
    class Int(object):
        not_none = Integer(1, allow_none=False)
        positive = Integer(validators=positive)

    def test_not_none(self):
        with nose.tools.assert_raises(ValueError):
            self.Int(not_none=None)

    def test_positive(self):
        with nose.tools.assert_raises(ValueError):
            self.Int(positive=-1)
        assert self.Int(positive=2).positive == 2


class TestNumber(TestCase):

    @attr.s
    class N(object):
        default = Number(1.5)
        positive = Number(validators=positive)
        between = Number(validators=between(0, 1))

    def test_positive(self):
        with nose.tools.assert_raises(ValueError):
            self.N(positive=-15)
        assert self.N(positive=15).positive == 15

    def test_between(self):
        with nose.tools.assert_raises(ValueError):
            self.N(between=-1)
        assert self.N(between=0.5).between == 0.5

    def test_default(self):
        assert self.N().default == 1.5


class TestPoints(TestCase):

    @attr.s
    class P(object):
        default = Points()
        not_none = Points([[1, 2]], allow_none=False)

    def test_default(self):
        p = self.P()
        assert p.not_none == [[1, 2]]
        assert p.default is None

    def test_not_none(self):
        with nose.tools.assert_raises(ValueError):
            self.P(not_none=None)

    def test_not_points(self):
        with nose.tools.assert_raises(ValueError):
            self.P(default=[[1, 'a']])

    def test_points(self):
        points = [[1, 1], [1.5, 1.5]]
        p = self.P(default=points)
        assert p.default == points


class TestString(TestCase):

    @attr.s
    class S(object):
        default = String()
        not_none = String('s', allow_none=False)

    def test_default(self):
        s = self.S()
        assert s.default is None
        assert s.not_none == 's'

    def test_not_none(self):
        with nose.tools.assert_raises(ValueError):
            self.S(not_none=None)
