from unittest import TestCase

from . import files
from pdf_annotate import PdfAnnotator


class TestPdf(TestCase):

    def test_get_page(self):
        pass

    def test_get_page_out_of_bounds(self):
        pass

    def test_get_rotation(self):
        pass


class TestPdfAnnotator(TestCase):

    def test_get_size(self):
        a = PdfAnnotator(files.SIMPLE)
        size = a.get_size(0)
        assert size == (612.0, 792.0)

    def test_get_annotation(self):
        pass

    def test_get_annotation_scaled(self):
        pass

    def test_get_annotation_page_dimensions(self):
        pass

    def test_get_annotation_rotated(self):
        pass

    def test_write(self):
        pass
