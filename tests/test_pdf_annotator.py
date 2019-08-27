# -*- coding: utf-8 -*-
from unittest import TestCase

from pdfrw import PdfReader

from pdf_annotate import Appearance
from pdf_annotate import Location
from pdf_annotate import PdfAnnotator
from pdf_annotate.util.geometry import identity
from pdf_annotate.util.geometry import translate
from tests import files
from tests.utils import assert_matrices_equal
from tests.utils import load_annotations_from_pdf
from tests.utils import write_to_temp


class TestPdfAnnotator(TestCase):

    def test_init_with_reader(self):
        a = PdfAnnotator(PdfReader(files.SIMPLE))
        assert a._pdf is not None

    def test_write_with_compress_off_smoke_test(self):
        a = PdfAnnotator(PdfReader(files.SIMPLE), compress=False)
        with write_to_temp(a) as t:
            assert load_annotations_from_pdf(t) is None

    def test_get_page_bounding_box(self):
        a = PdfAnnotator(files.SIMPLE)
        # The simple file has both MediaBox and CropBox set to the same value
        assert a.get_page_bounding_box(0) == [0, 0, 612, 792]

        page = a._pdf.get_page(0)

        # Still works without CropBox
        page.CropBox = None
        assert a.get_page_bounding_box(0) == [0, 0, 612, 792]
        page.MediaBox = [1, 1, 611, 791]
        assert a.get_page_bounding_box(0) == [1, 1, 611, 791]

        # But CropBox takes precedence
        page.CropBox = [12, 16, 600, 792]
        assert a.get_page_bounding_box(0) == [12, 16, 600, 792]

    def test_get_size(self):
        a = PdfAnnotator(files.SIMPLE)
        size = a.get_size(0)
        assert size == (612.0, 792.0)

    def test_get_rotation(self):
        assert PdfAnnotator(files.SIMPLE).get_rotation(0) == 0
        assert PdfAnnotator(files.ROTATED_90).get_rotation(0) == 90

    def test_get_scale_default(self):
        a = PdfAnnotator(files.SIMPLE)
        assert a.get_scale(0) == (1, 1)

    def test_get_scale_from_init(self):
        a = PdfAnnotator(files.SIMPLE, scale=0.48)
        assert a.get_scale(0) == (0.48, 0.48)

    def test_get_scale_from_page_dimensions(self):
        a = PdfAnnotator(files.SIMPLE)
        # Rastered at different X and Y scales. Why would you do that?
        a.set_page_dimensions((1275, 3300), 0)
        assert a.get_scale(0) == (0.48, 0.24)

    def test_get_rotated_scale_from_dimensions(self):
        a = PdfAnnotator(files.ROTATED_90)
        a.set_page_dimensions((3300, 1275), 0)
        assert a.get_scale(0) == (0.24, 0.48)

    def test_add_annotation_page_dimensions(self):
        # Ensure that changing a page's dimensions results in annotations being
        # placed in the proper locations.
        a = PdfAnnotator(files.SIMPLE)
        # Act like the PDF was rastered at 144 DPI (2x default user space)
        a.set_page_dimensions((1224, 1584), 0)
        a.add_annotation(
            'square',
            Location(x1=10, y1=20, x2=20, y2=30, page=0),
            Appearance(),
        )
        with write_to_temp(a) as t:
            annotations = load_annotations_from_pdf(t)

        square = annotations.pop()
        assert len(annotations) == 0
        assert square.Subtype == '/Square'
        # The outer bounding box of the square is padded outward by the stroke
        # width, and then scaled down by two.
        self.assertEqual(square.Rect, ['4.5', '9.5', '10.5', '15.5'])


class TestPdfAnnotatorGetTransform(TestCase):

    def test_identity(self):
        t = PdfAnnotator._get_transform(
            bounding_box=[0, 0, 100, 200],
            rotation=0,
            _scale=(1, 1),
        )
        assert t == identity()

    def _assert_transform(
        self,
        expected,
        rotation=0,
        scale=(1, 1),
        bounding_box=None,
    ):
        bounding_box = bounding_box or [0, 0, 100, 200]
        t = PdfAnnotator._get_transform(
            bounding_box=bounding_box,
            rotation=rotation,
            _scale=scale,
        )
        assert_matrices_equal(t, expected)

    def test_rotated(self):
        self._assert_transform([0, 1, -1, 0, 100, 0], rotation=90)
        self._assert_transform([-1, 0, 0, -1, 100, 200], rotation=180)
        self._assert_transform([0, -1, 1, 0, 0, 200], rotation=270)

    def test_scaled(self):
        self._assert_transform([2, 0, 0, 4, 0, 0], scale=(2, 4))

    def test_scale_rotate(self):
        self._assert_transform(
            [0, 2, -4, 0, 100, 0],
            scale=(2, 4),
            rotation=90,
        )

    def test_weird_bounding_box(self):
        self._assert_transform(translate(0, -30), bounding_box=[0, -30, 20, 0])

    def test_weird_bounding_box_rotated(self):
        self._assert_transform(
            [0, 1, -1, 0, 20, -30],
            bounding_box=[0, -30, 20, 0],
            rotation=90,
        )

    def test_weird_bounding_box_scaled(self):
        self._assert_transform(
            [2, 0, 0, 4, 0, -30],
            bounding_box=[0, -30, 20, 0],
            scale=(2, 4),
        )
