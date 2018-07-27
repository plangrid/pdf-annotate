# -*- coding: utf-8 -*-
from unittest import TestCase

from . import files
from pdf_annotate import PdfAnnotator
from pdf_annotate.utils import identity
from pdf_annotate.utils import translate


def assert_matrices_equal(m, n):
    _m = [round(v, 7) for v in m]
    _n = [round(v, 7) for v in n]
    assert _m == _n


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

    def test_get_annotation_page_dimensions(self):
        pass

    def test_get_annotation_rotated(self):
        pass

    def test_write(self):
        pass


class TestPdfAnnotatorGetTransform(TestCase):

    def test_identity(self):
        t = PdfAnnotator._get_transform(
            media_box=[0, 0, 100, 200],
            rotation=0,
            dimensions=None,
            _scale=(1, 1),
        )
        assert t == identity()

    def _assert_transform(
        self,
        expected,
        rotation=0,
        scale=(1, 1),
        dimensions=None,
        media_box=None,
    ):
        media_box = media_box or [0, 0, 100, 200]
        t = PdfAnnotator._get_transform(
            media_box=media_box,
            rotation=rotation,
            dimensions=dimensions,
            _scale=scale,
        )
        assert_matrices_equal(t, expected)

    def test_rotated(self):
        self._assert_transform([0, 1, -1, 0, 100, 0], rotation=90)
        self._assert_transform([-1, 0, 0, -1, 100, 200], rotation=180)
        self._assert_transform([0, -1, 1, 0, 0, 200], rotation=270)

    def test_scaled(self):
        self._assert_transform([2, 0, 0, 4, 0, 0], scale=(2, 4))

    def test_dimensions(self):
        self._assert_transform([2, 0, 0, 4, 0, 0], dimensions=(50, 50))
        self._assert_transform([0.5, 0, 0, 0.5, 0, 0], dimensions=(200, 400))

    def test_scale_rotate(self):
        self._assert_transform([0, 2, -4, 0, 100, 0], scale=(2, 4), rotation=90)

    def test_weird_media_box(self):
        self._assert_transform(translate(0, -30), media_box=[0, -30, 20, 0])

    def test_weird_media_box_rotated(self):
        self._assert_transform(
            [0, 1, -1, 0, 20, -30],
            media_box=[0, -30, 20, 0],
            rotation=90,
        )

    def test_weird_media_box_scaled(self):
        self._assert_transform(
            [2, 0, 0, 4, 0, -30],
            media_box=[0, -30, 20, 0],
            scale=(2, 4),
        )
