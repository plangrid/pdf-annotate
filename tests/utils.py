# -*- coding: utf-8 -*-
import os
import tempfile
from contextlib import contextmanager

from pdfrw import PdfReader


def load_annotations_from_pdf(filename, page=0):
    reader = PdfReader(filename)
    return reader.pages[page].Annots


@contextmanager
def write_to_temp(annotator):
    t = tempfile.mktemp(suffix='.pdf')
    annotator.write(t)
    try:
        yield t
    finally:
        os.remove(t)


def assert_matrices_equal(a, b):
    for i, j in zip(a, b):
        assert abs(i - j) <= 1e-10
