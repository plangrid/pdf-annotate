# -*- coding: utf-8 -*-
from pdf_annotate.annotator import PdfAnnotator
from tests.files import SIMPLE


ANNOTATORS = {}


def setUpModule():
    # For unit tests that still require a functional PdfAnnotator object, we
    # instantiate a global annotator at the module level.
    ANNOTATORS['simple'] = PdfAnnotator(SIMPLE)
