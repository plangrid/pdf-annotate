import os.path
from unittest import TestCase

import pdfrw

from pdf_annotate import Appearance
from pdf_annotate import Location
from pdf_annotate import PdfAnnotator
from tests.files import PNG_FILES
from tests.files import ROTATED_90
from tests.files import SIMPLE


class EndToEndMixin(object):
    """End to end test of PdfAnnotator.

    To truly test PDF annotations end to end, you need to do some sort of
    visual inspection. There are several options, including rastering the PDF
    and doing pixel diffs. Until we end up doing something like this, the end-
    to-end test will be a tiny amount of validation in code + manual inspection
    of the output.
    """

    def setUp(self):
        self.gaudy = Appearance(
            stroke_color=[1, 0, 0],
            stroke_width=3,
            fill=[0, 1, 0],
            text='Taco tuesday',
            font_size=12,
            wrap_text=True,
        )

        self.long_text = self.gaudy.copy()
        self.long_text.stroke_color = [0, 0, 0]
        self.long_text.text = "Though yet of Hamlet, our dear brother's death"
        self.long_text.font_size = 7

        self.no_wrap_text = self.long_text.copy()
        self.no_wrap_text.stroke_color = [0, 1, 1]
        self.no_wrap_text.wrap_text = False

    def test_end_to_end(self):
        a = PdfAnnotator(self.INPUT_FILENAME)
        self._add_annotations(a)
        output_file = self._get_output_file()
        a.write(output_file)
        self._check_num_annotations(output_file)

    def _check_num_annotations(self, output_file):
        f = pdfrw.PdfReader(output_file)
        assert len(f.pages[0].Annots) == 13

    def _get_output_file(self):
        dirname, _ = os.path.split(os.path.abspath(__file__))
        return os.path.join(dirname, 'pdfs', self.OUTPUT_FILENAME)

    def _add_annotations(self, a):
        self._add_shape_annotations(a)
        self._add_image_annotations(a)
        self._add_text_annotations(a)

    def _add_shape_annotations(self, a):
        a.add_annotation(
            'square',
            Location(x1=10, y1=20, x2=50, y2=60, page=0),
            self.gaudy,
        )
        a.add_annotation(
            'circle',
            Location(x1=60, y1=20, x2=100, y2=60, page=0),
            self.gaudy,
        )
        a.add_annotation(
            'polygon',
            Location(points=[[110, 20], [150, 20], [130, 60]], page=0),
            self.gaudy,
        )
        a.add_annotation(
            'polyline',
            Location(points=[[160, 20], [200, 20], [180, 60]], page=0),
            self.gaudy,
        )
        a.add_annotation(
            'line',
            Location(points=[[210, 20], [250, 60]], page=0),
            self.gaudy,
        )
        a.add_annotation(
            'ink',
            Location(points=[[260, 20], [300, 60]], page=0),
            self.gaudy,
        )

    def _add_image_annotations(self, a):
        xs = [10, 60, 110, 160]
        for x, image_file in zip(xs, PNG_FILES):
            a.add_annotation(
                'image',
                Location(x1=x, y1=70, x2=(x + 40), y2=110, page=0),
                Appearance(stroke_width=0, image=image_file),
            )

    def _add_text_annotations(self, a):
        xs = [10, 60, 110]
        appearances = [self.gaudy, self.long_text, self.no_wrap_text]
        for x, appearance in zip(xs, appearances):
            a.add_annotation(
                'text',
                Location(x1=x, y1=120, x2=(x + 40), y2=160, page=0),
                appearance,
            )


class TestEndToEnd(EndToEndMixin, TestCase):
    INPUT_FILENAME = SIMPLE
    OUTPUT_FILENAME = 'end_to_end.pdf'


class TestEndToEndRotated(EndToEndMixin, TestCase):
    INPUT_FILENAME = ROTATED_90
    OUTPUT_FILENAME = 'end_to_end_rotated_90.pdf'
