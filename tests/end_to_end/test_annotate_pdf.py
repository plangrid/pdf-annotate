# -*- coding: utf-8 -*-
import os.path
from unittest import TestCase

import pdfrw

from pdf_annotate import Appearance
from pdf_annotate import Location
from pdf_annotate import PdfAnnotator
from pdf_annotate.annotations.image import Image
from pdf_annotate.config import constants
from pdf_annotate.config.graphics_state import GraphicsState
from pdf_annotate.graphics import ContentStream
from pdf_annotate.graphics import CTM
from pdf_annotate.graphics import GraphicsState as CSGraphicsState
from pdf_annotate.graphics import Line
from pdf_annotate.graphics import Move
from pdf_annotate.graphics import Rect
from pdf_annotate.graphics import Restore
from pdf_annotate.graphics import Save
from pdf_annotate.graphics import Stroke
from pdf_annotate.graphics import StrokeColor
from pdf_annotate.graphics import StrokeWidth
from pdf_annotate.graphics import XObject
from tests.files import PNG_FILES
from tests.files import ROTATED_180
from tests.files import ROTATED_270
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
    EXPECTED_ANNOTATIONS = 35

    def setUp(self):
        self.gaudy = Appearance(
            stroke_color=[1, 0, 0],
            stroke_width=3,
            fill=[0, 1, 0],
            content='Latin',
            font_size=12,
            wrap_text=True,
        )

        self.transparent = self.gaudy.copy(
            fill=[0, 0, 1, 0.5],
            stroke_color=[1, 0, 0, 0.25],
        )

        self.top_left = self.gaudy.copy(
            stroke_color=[0, 0, 0],
            content=(
                r"Though yet of Hamlet, our dear brother's death \\ "
                r"The memory be green"
            ),
            font_size=6,
            text_align='left',
            text_baseline='top',
        )
        self.top_center = self.top_left.copy(text_align='center')
        self.top_right = self.top_left.copy(text_align='right')

        self.middle_left = self.top_left.copy(text_baseline='middle')
        self.middle_center = self.middle_left.copy(text_align='center')
        self.middle_right = self.middle_left.copy(text_align='right')

        self.bottom_left = self.top_left.copy(text_baseline='bottom')
        self.bottom_center = self.bottom_left.copy(text_align='center')
        self.bottom_right = self.bottom_left.copy(text_align='right')

        self.texts = [
            self.top_left, self.top_center, self.top_right,
            self.middle_left, self.middle_center, self.middle_right,
            self.bottom_left, self.bottom_center, self.bottom_right,
        ]

        self.image_appearance = Appearance(stroke_width=0)
        self.transparent_image_appearance = self.image_appearance.copy(
            fill_transparency=0.5,
            stroke_transparency=0.5,
        )

    def test_end_to_end(self):
        a = PdfAnnotator(self.INPUT_FILENAME)
        self._add_annotations(a)
        output_file = self._get_output_file()
        a.write(output_file)
        self._check_num_annotations(output_file)

    def _check_num_annotations(self, output_file):
        f = pdfrw.PdfReader(output_file)
        assert len(f.pages[0].Annots) == self.EXPECTED_ANNOTATIONS

    def _get_output_file(self):
        dirname, _ = os.path.split(os.path.abspath(__file__))
        return os.path.join(dirname, 'pdfs', self.OUTPUT_FILENAME)

    def _add_annotations(self, a):
        # Original page size (612, 792)
        self._add_shape_annotations(a, self.gaudy)
        self._add_shape_annotations(a, self.transparent, y1=70, y2=110)
        self._add_image_annotations(a, self.image_appearance)
        self._add_image_annotations(
            a,
            self.transparent_image_appearance,
            y1=170,
            y2=210,
        )
        self._add_text_annotations(a)
        self._add_explicit_image_annotation(a)
        self._add_explicit_graphics_state_annotation(a)

    def _add_shape_annotations(self, a, appearance, y1=20, y2=60):
        a.add_annotation(
            'square',
            Location(x1=10, y1=y1, x2=50, y2=y2, page=0),
            appearance,
        )
        a.add_annotation(
            'circle',
            Location(x1=60, y1=y1, x2=100, y2=y2, page=0),
            appearance,
        )
        a.add_annotation(
            'polygon',
            Location(points=[[110, y1], [150, y1], [130, y2]], page=0),
            appearance,
        )
        a.add_annotation(
            'polyline',
            Location(points=[[160, y1], [200, y1], [180, y2]], page=0),
            appearance,
        )
        a.add_annotation(
            'line',
            Location(points=[[210, y1], [250, y2]], page=0),
            appearance,
        )
        a.add_annotation(
            'ink',
            Location(points=[[260, y1], [300, y2]], page=0),
            appearance,
        )

        round = appearance.copy(line_cap=constants.LINE_CAP_ROUND)
        a.add_annotation(
            'line',
            location=Location(points=[[310, y1], [350, y2]], page=0),
            appearance=round,
        )

        dashed = appearance.copy(dash_array=[[3], 0])
        a.add_annotation(
            'line',
            location=Location(points=[[360, y1], [400, y2]], page=0),
            appearance=dashed,
        )

    def _add_image_annotations(self, a, appearance, y1=120, y2=160):
        xs = [10, 60, 110, 160]
        for x, image_file in zip(xs, PNG_FILES):
            a.add_annotation(
                'image',
                Location(x1=x, y1=y1, x2=(x + 40), y2=y2, page=0),
                appearance.copy(image=image_file),
            )

    def _add_text_annotations(self, a, y1=220, y2=300):
        xs = [10 + (i * 50) for i in range(len(self.texts))]
        for x, appearance in zip(xs, self.texts):
            a.add_annotation(
                'text',
                Location(x1=x, y1=y1, x2=(x + 40), y2=y2, page=0),
                appearance,
            )

    def _add_explicit_image_annotation(self, a):
        """Add an image annotation using ContentStream commands instead of the
        Image type's commands. This is testing that the external XObjects API
        works, and that images can be embedded inside other, more complex
        annotations.
        """
        x1, y1, x2, y2 = 10, 310, 50, 350
        location = Location(x1=x1, y1=y1, x2=x2, y2=y2, page=0)

        content_stream = ContentStream([
            StrokeColor(1, 0, 0),
            Rect(x1, y1, x2 - x1, y2 - y1),
            Save(),
            # The image is inside an outer rectangle
            CTM(Image.get_ctm(x1 + 10, y1 + 10, x2 - 10, y2 - 10)),
            XObject('MyXObject'),
            Restore(),
            Stroke(),
        ])
        appearance = Appearance(
            appearance_stream=content_stream,
            xobjects={
                'MyXObject': Image.make_image_xobject(PNG_FILES[0]),
            },
        )

        a.add_annotation(
            'square',
            location=location,
            appearance=appearance,
        )

    def _add_explicit_graphics_state_annotation(self, a):
        graphics_states = {
            'BevelSquare': GraphicsState(
                line_join=constants.LINE_JOIN_BEVEL,
                line_cap=constants.LINE_CAP_SQUARE,
                stroke_transparency=0.75,
            ),
            'MiterButt': GraphicsState(
                line_join=constants.LINE_JOIN_MITER,
                line_cap=constants.LINE_CAP_BUTT,
                stroke_transparency=0.5,
            ),
            'RoundRound': GraphicsState(
                line_join=constants.LINE_JOIN_ROUND,
                line_cap=constants.LINE_CAP_ROUND,
                stroke_transparency=0.25,
            ),
        }

        # Defines the bounding box of the chevrons
        x1, y1, x2, y2 = 60, 310, 100, 350
        lines_location = Location(x1=x1, y1=y1, x2=x2, y2=y2, page=0)

        # Defines the start/end of the chevrons
        x1, midpoint, x2 = 65, 80, 95
        y1 = 315

        content_stream = ContentStream([
            Save(),
            StrokeWidth(5),

            CSGraphicsState('BevelSquare'),
            Move(x1, y1),
            Line(midpoint, y1 + 10),
            Line(x2, y1),
            Stroke(),

            CSGraphicsState('MiterButt'),
            Move(x1, y1 + 10),
            Line(midpoint, y1 + 20),
            Line(x2, y1 + 10),
            Stroke(),

            CSGraphicsState('RoundRound'),
            Move(x1, y1 + 20),
            Line(midpoint, y1 + 30),
            Line(x2, y1 + 20),
            Stroke(),

            Restore(),
        ])
        appearance = Appearance(
            appearance_stream=content_stream,
            graphics_states=graphics_states,
        )
        a.add_annotation(
            'square',
            location=lines_location,
            appearance=appearance,
        )


class TestEndToEnd(EndToEndMixin, TestCase):
    INPUT_FILENAME = SIMPLE
    OUTPUT_FILENAME = 'end_to_end.pdf'


class TestEndToEndRotated90(EndToEndMixin, TestCase):
    INPUT_FILENAME = ROTATED_90
    OUTPUT_FILENAME = 'end_to_end_rotated_90.pdf'


class TestEndToEndRotated180(EndToEndMixin, TestCase):
    INPUT_FILENAME = ROTATED_180
    OUTPUT_FILENAME = 'end_to_end_rotated_180.pdf'


class TestEndToEndRotated270(EndToEndMixin, TestCase):
    INPUT_FILENAME = ROTATED_270
    OUTPUT_FILENAME = 'end_to_end_rotated_270.pdf'
