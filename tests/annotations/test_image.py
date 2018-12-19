# -*- coding: utf-8 -*-
from unittest import TestCase

from pdf_annotate.annotations.image import Image
from pdf_annotate.config.appearance import Appearance
from pdf_annotate.config.location import Location
from pdf_annotate.util.geometry import identity
from pdf_annotate.util.geometry import translate
from tests.files import PNG_FILES


class TestImage(TestCase):

    def test_as_pdf_object(self):
        x1, y1, x2, y2 = 10, 20, 100, 200
        image = Image(
            location=Location(x1=x1, y1=y1, x2=x2, y2=y2, page=0),
            appearance=Appearance(stroke_width=0, image=PNG_FILES[0]),
        )
        obj = image.as_pdf_object(identity(), page=None)
        # Appearance stream should place the Image correctly
        assert obj.AP.N.stream == (
            'q 0 0 0 RG 0 w 10 20 90 180 re 90 0 0 180 10 20 cm /Image Do Q'
        )
        assert obj.Rect == [x1, y1, x2, y2]
        assert obj.AP.N.BBox == [x1, y1, x2, y2]
        assert obj.AP.N.Matrix == translate(-x1, -y1)


class TestMakeImageXObject(TestCase):

    def test_filenane(self):
        pass

    def test_png(self):
        pass

    def test_jpeg(self):
        pass

    def test_gif(self):
        pass

    def test_png_conversion(self):
        pass

    def test_jpeg_conversion(self):
        pass
