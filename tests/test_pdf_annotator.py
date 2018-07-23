from unittest import TestCase

from . import files
from pdf_annotate import PdfAnnotator


class TestPdfAnnotator(TestCase):

    def test_get_size(self):
        a = PdfAnnotator(files.SIMPLE)
        size = a.get_size(0)
        assert size == (612.0, 792.0)
