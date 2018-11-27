# -*- coding: utf-8 -*-
from unittest import TestCase

from pdf_annotate.config.appearance import Appearance


class TestAppearance(TestCase):

    def test_explicit_transparency(self):
        a = Appearance(
            fill=[0, 0, 0],
            fill_transparency=0.5,
            stroke_color=[0, 0, 0],
            stroke_transparency=0.25,
        )
        state = a.get_graphics_state()
        assert state.fill_transparency == 0.5
        assert state.stroke_transparency == 0.25

    def test_implicit_transparency(self):
        a = Appearance(
            fill=[0, 0, 0, 0.5],
            stroke_color=[0, 0, 0, 0.25],
        )
        state = a.get_graphics_state()
        assert state.fill_transparency == 0.5
        assert state.stroke_transparency == 0.25

    def test_copy(self):
        a = Appearance(stroke_width=10, miter_limit=1.5)
        b = a.copy(miter_limit=1.6)
        assert b.stroke_width == 10
        assert b.miter_limit == 1.6
