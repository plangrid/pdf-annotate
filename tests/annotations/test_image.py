# -*- coding: utf-8 -*-
from unittest import TestCase

from PIL import Image as PILImage
from PIL import ImageDraw

from pdf_annotate.annotations.image import Image
from pdf_annotate.config.appearance import Appearance
from pdf_annotate.config.constants import GRAYSCALE_ALPHA_MODE
from pdf_annotate.config.constants import GRAYSCALE_MODE
from pdf_annotate.config.location import Location
from pdf_annotate.util.geometry import identity
from pdf_annotate.util.geometry import translate
from tests.files import GRAYSCALE_PNG
from tests.files import PNG_FILES


def add_alpha(image):
    """Adds an alpha layer to an existing PIL image."""
    new_image = image.copy()
    mask = PILImage.new(GRAYSCALE_MODE, new_image.size, color=255)
    width, height = new_image.size
    ImageDraw.Draw(mask).rectangle(
        (width / 2.0, height / 2.0, width, height),
        fill=0,
    )
    new_image.putalpha(mask)
    return new_image


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


class TestImageModes(TestCase):

    @classmethod
    def setup_class(cls):
        cls.grayscale_image = PILImage.open(GRAYSCALE_PNG)
        assert cls.grayscale_image.mode == GRAYSCALE_MODE
        assert cls.grayscale_image.format == 'PNG'

    def test_convert_noop(self):
        image, smask = Image.convert_to_compatible_image(
            self.grayscale_image,
            'PNG',
        )
        assert image.mode == GRAYSCALE_MODE
        assert smask is None

    def test_convert_grayscale_with_alpha(self):
        image = add_alpha(self.grayscale_image)
        assert image.mode == GRAYSCALE_ALPHA_MODE

        appropriate_image, smask = Image.convert_to_compatible_image(
            image,
            'PNG',
        )
        assert appropriate_image.mode == GRAYSCALE_MODE
        assert smask.Width == image.size[0]
        assert smask.Height == image.size[1]
