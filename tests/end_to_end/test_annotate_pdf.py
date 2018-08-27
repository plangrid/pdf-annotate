import os.path
from unittest import TestCase

import pdfrw

from pdf_annotate import Appearance
from pdf_annotate import Location
from pdf_annotate import Metadata
from pdf_annotate import PdfAnnotator
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
            text='Latin',
            font_size=12,
        )

    def test_end_to_end(self):
        a = PdfAnnotator(self.INPUT_FILENAME)
        self._add_annotations(a)
        output_file = self._get_output_file()
        a.write(output_file)
        self._check_num_annotations(output_file)

    def _check_num_annotations(self, output_file):
        f = pdfrw.PdfReader(output_file)
        assert len(f.pages[0].Annots) == 7

    def _get_output_file(self):
        dirname, _ = os.path.split(os.path.abspath(__file__))
        return os.path.join(dirname, 'pdfs', self.OUTPUT_FILENAME)

    def _add_annotations(self, a):
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
        a.add_annotation(
            'text',
            Location(x1=310, y1=20, x2=350, y2=60, page=0),
            self.gaudy,
        )


class TestEndToEnd(EndToEndMixin, TestCase):
    INPUT_FILENAME = SIMPLE
    OUTPUT_FILENAME = 'end_to_end.pdf'


class TestEndToEndRotated(EndToEndMixin, TestCase):
    INPUT_FILENAME = ROTATED_90
    OUTPUT_FILENAME = 'end_to_end_rotated_90.pdf'
