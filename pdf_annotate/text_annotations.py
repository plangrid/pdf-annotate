# -*- coding: utf-8 -*-
"""
FreeText annotation.
"""
import os.path

from PIL import ImageFont

from pdf_annotate.annotations import _make_border_dict
from pdf_annotate.annotations import Annotation
from pdf_annotate.graphics import BeginText
from pdf_annotate.graphics import ContentStream
from pdf_annotate.graphics import CTM
from pdf_annotate.graphics import EndText
from pdf_annotate.graphics import FillColor
from pdf_annotate.graphics import Font
from pdf_annotate.graphics import Restore
from pdf_annotate.graphics import Save
from pdf_annotate.graphics import StrokeColor
from pdf_annotate.graphics import StrokeWidth
from pdf_annotate.graphics import Text
from pdf_annotate.graphics import TextMatrix
from pdf_annotate.rect_annotations import RectAnnotation
from pdf_annotate.utils import get_wrapped_lines
from pdf_annotate.utils import rotate
from pdf_annotate.utils import translate


PDF_ANNOTATOR_FONT = 'PDFANNOTATORFONT1'

HELVETICA_PATH = os.path.join(
    os.path.dirname(__file__),
    'fonts',
    'Helvetica.ttf',
)


class FreeText(Annotation):
    """FreeText annotation. Right now, we only support writing text in the
    Helvetica font. Dealing with fonts is tricky business, so we'll leave that
    for later.
    """
    subtype = 'FreeText'
    font = PDF_ANNOTATOR_FONT

    @staticmethod
    def transform(location, transform):
        return RectAnnotation.transform(location, transform)

    def get_matrix(self):
        L = self._location
        return translate(-L.x1, -L.y1)

    def make_rect(self):
        L = self._location
        return [L.x1, L.y1, L.x2, L.y2]

    def make_default_appearance(self):
        """Returns a DA string for the text object, e.g. '1 0 0 rg /Helv 12 Tf'
        """
        A = self._appearance
        stream = ContentStream([
            StrokeColor(*A.stroke_color),
            Font(self.font, A.font_size),
        ])
        return stream.resolve()

    def as_pdf_object(self):
        obj = self.make_base_object()
        obj.Contents = self._appearance.text
        obj.DA = self.make_default_appearance()
        obj.C = []
        # TODO allow setting border on free text boxes
        obj.BS = _make_border_dict(width=0, style='S')
        # TODO DS is required to have BB not redraw the annotation in their own
        # style when you edit it.
        return obj

    def graphics_commands(self):
        A = self._appearance
        L = self._location

        stream = ContentStream([
            Save(),
            CTM(self._get_graphics_cm()),
            # Not quite sure why we write black + the stroke color before BT
            StrokeColor(1, 1, 1),
            FillColor(*A.stroke_color),
            StrokeWidth(0),
            BeginText(),
            StrokeColor(*A.stroke_color),
            Font(self.font, A.font_size),
        ])
        stream.extend(get_text_commands(
            L.x1, L.y1, L.x2, L.y2,
            text=A.text,
            font_size=A.font_size,
            rotation=self._rotation,
            wrap_text=A.wrap_text,
        ))
        stream.extend([
            EndText(),
            Restore(),
        ])

        return stream.resolve()

    def _get_graphics_cm(self):
        return rotate(self._rotation)


def get_text_commands(x1, y1, x2, y2, text, font_size, rotation, wrap_text):
    """Return the graphics stream commands necessary to render a free text
    annotation, given the various parameters.

    :param number x1: bounding box lower left x
    :param number y1: bounding box lower left y
    :param number x2: bounding box upper right x
    :param number y2: bounding box upper right y
    :param str text: text to add to annotation
    :param number font_size: font size
    :param int rotation: page's rotation, int that's a multiple of 90
    :param bool wrap_text: whether to wrap the text
    """
    tm = _get_text_matrix(x1, y1, x2, y2, font_size, rotation)
    if wrap_text:
        font = ImageFont.truetype(HELVETICA_PATH, size=font_size)
        width = x2 - x1
        line_spacing = 1.2 * font_size

        lines = get_wrapped_lines(
            text,
            lambda text: font.getsize(text)[0],
            width,
        )
        commands = []
        # For each line of wrapped text, adjust the text matrix to go down to
        # the next line.
        for line in lines:
            commands.extend([
                TextMatrix(tm),
                Text(line),
            ])
            tm = translate(tm[4], tm[5] - line_spacing)
        return commands
    else:
        return [
            TextMatrix(tm),
            Text(text),
        ]


def _get_text_matrix(x1, y1, x2, y2, font_size, rotation):
    # Not entirely sure what y offsets I should be calculating here.
    if rotation == 0:
        return translate(x1 + 1, y2 - font_size)
    elif rotation == 90:
        return translate(y1 + 1, -(x1 + font_size))
    elif rotation == 180:
        return translate(-x2 + 1, -(y1 + font_size))
    else:  # 270
        return translate(-y2 + 1, x2 - font_size)
