# -*- coding: utf-8 -*-
from unittest import TestCase

import pytest
from pdfrw import PdfDict
from pdfrw import PdfName

from pdf_annotate.config import constants
from pdf_annotate.config.graphics_state import GraphicsState


class TestGraphicsState(TestCase):

    def test_blank(self):
        pdf_dict = GraphicsState().as_pdf_dict()
        assert len(pdf_dict) == 1
        assert pdf_dict.Type == PdfName('ExtGState')

    def test_graphics_state(self):
        state = GraphicsState(
            line_width=2,
            line_cap=constants.LINE_CAP_ROUND,
            line_join=constants.LINE_JOIN_MITER,
            miter_limit=1.404,
            dash_array=[[1], 0],
            stroke_transparency=0.7,
            fill_transparency=0.5,
        )
        pdf_dict = state.as_pdf_dict()
        assert pdf_dict == PdfDict(
            Type=PdfName('ExtGState'),
            LW=2,
            LC=1,
            LJ=0,
            ML=1.404,
            D=[[1], 0],
            CA=0.7,
            ca=0.5,
        )

    def test_dash_array(self):
        with pytest.raises(ValueError):
            GraphicsState(dash_array=[1, 1])
        with pytest.raises(ValueError):
            GraphicsState(dash_array=[[1.5], 1])
        with pytest.raises(ValueError):
            GraphicsState(dash_array='--- 1')

        state = GraphicsState(dash_array=[[2, 1], 1])
        assert state.dash_array == [[2, 1], 1]

    def test_has_content(self):
        assert not GraphicsState().has_content()
        assert GraphicsState(line_width=2).has_content()
