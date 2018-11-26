# -*- coding: utf-8 -*-
from unittest import TestCase

from pdfrw import PdfName

from pdf_annotate.config.graphics_state import GraphicsState


class TestGraphicsState(TestCase):

    def test_blank(self):
        pdf_dict = GraphicsState().as_pdf_dict()
        assert len(pdf_dict) == 1
        assert pdf_dict.Type == PdfName('ExtGState')
