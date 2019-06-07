# -*- coding: utf-8 -*-
"""
    Text Annotations
    ~~~~~~~~~~~~~~~~
    The FreeText annotation

    :copyright: Copyright 2019 Autodesk, Inc.
    :license: MIT, see LICENSE for details.
"""
import os.path

from pdfrw import PdfDict
from pdfrw import PdfName
from PIL import ImageFont

from pdf_annotate.annotations.base import _make_border_dict
from pdf_annotate.annotations.base import Annotation
from pdf_annotate.config.constants import DEFAULT_BASE_FONT
from pdf_annotate.config.constants import GRAPHICS_STATE_NAME
from pdf_annotate.config.constants import PDF_ANNOTATOR_FONT
from pdf_annotate.graphics import BeginText
from pdf_annotate.graphics import ContentStream
from pdf_annotate.graphics import EndText
from pdf_annotate.graphics import FillColor
from pdf_annotate.graphics import Font
from pdf_annotate.graphics import GraphicsState as CSGraphicsState
from pdf_annotate.graphics import Restore
from pdf_annotate.graphics import Save
from pdf_annotate.graphics import Text
from pdf_annotate.graphics import TextMatrix
from pdf_annotate.util.geometry import translate
from pdf_annotate.util.text import get_wrapped_lines


HELVETICA_PATH = os.path.join(
    os.path.dirname(__file__),
    '..',
    'fonts',
    'Helvetica.ttf',
)


class FreeText(Annotation):
    """FreeText annotation. Right now, we only support writing text in the
    Helvetica font. Dealing with fonts is tricky business, so we'll leave that
    for later.
    """
    subtype = 'FreeText'

    def make_rect(self):
        L = self._location
        return [L.x1, L.y1, L.x2, L.y2]

    def make_default_appearance(self):
        """Returns a DA string for the text object, e.g. '1 0 0 rg /Helv 12 Tf'
        """
        A = self._appearance
        stream = ContentStream([
            FillColor(*A.fill[:3]),
            Font(PDF_ANNOTATOR_FONT, A.font_size),
        ])
        return stream.resolve()

    def add_additional_pdf_object_data(self, obj):
        obj.Contents = self._appearance.content
        obj.DA = self.make_default_appearance()
        obj.C = []
        # TODO allow setting border on free text boxes
        obj.BS = _make_border_dict(width=0, style='S')
        # TODO DS is required to have BB not redraw the annotation in their own
        # style when you edit it.

    @staticmethod
    def make_font_object():
        """Make a PDF Type1 font object for embedding in the annotation's
        Resources dict. Only Helvetica is supported as a base font.

        :returns PdfDict: Resources PdfDict object, ready to be included in the
            Resources 'Font' subdictionary.
        """
        return PdfDict(
            Type=PdfName('Font'),
            Subtype=PdfName('Type1'),
            BaseFont=PdfName(DEFAULT_BASE_FONT),
            Encoding=PdfName('WinAnsiEncoding'),
        )

    def add_additional_resources(self, resources):
        font_dict = PdfDict()
        font_dict[PdfName(PDF_ANNOTATOR_FONT)] = self.make_font_object()
        resources[PdfName('Font')] = font_dict

    def make_appearance_stream(self):
        A = self._appearance
        L = self._location

        stream = ContentStream([
            Save(),
            BeginText(),
            FillColor(*A.fill[:3]),
            Font(PDF_ANNOTATOR_FONT, A.font_size),
        ])

        graphics_state = A.get_graphics_state()
        if graphics_state.has_content():
            stream.add(CSGraphicsState(GRAPHICS_STATE_NAME))

        # Actually draw the text inside the rectangle
        stream.extend(get_text_commands(
            L.x1, L.y1, L.x2, L.y2,
            text=A.content,
            font_size=A.font_size,
            wrap_text=A.wrap_text,
            align=A.text_align,
            baseline=A.text_baseline,
            line_spacing=A.line_spacing,
        ))
        stream.extend([
            EndText(),
            Restore(),
        ])

        return stream


def get_text_commands(
    x1, y1, x2, y2,
    text, font_size, wrap_text,
    align, baseline, line_spacing,
):
    """Return the graphics stream commands necessary to render a free text
    annotation, given the various parameters.

    Text is optionally wrapped, then arranged according to align (horizontal
    alignment), and baseline (vertical alignment).

    :param number x1: bounding box lower left x
    :param number y1: bounding box lower left y
    :param number x2: bounding box upper right x
    :param number y2: bounding box upper right y
    :param str text: text to add to annotation
    :param number font_size: font size
    :param bool wrap_text: whether to wrap the text
    :param str align: 'left'|'center'|'right'
    :param str baseline: 'top'|'middle'|'bottom'
    :param number line_spacing: multiplier to determine line spacing
    """
    font = ImageFont.truetype(HELVETICA_PATH, size=int(round(font_size)))

    def measure(text): return font.getsize(text)[0]

    lines = get_wrapped_lines(text, measure, x2 - x1) if wrap_text else [text]
    # Line breaking cares about the whitespace in the string, but for the
    # purposes of laying out the broken lines, we want to measure the lines
    # without trailing/leading whitespace.
    lines = [line.strip() for line in lines]
    y_coords = _get_vertical_coordinates(
        lines,
        y1,
        y2,
        font_size,
        line_spacing,
        baseline,
    )
    xs = _get_horizontal_coordinates(lines, x1, x2, measure, align)
    commands = []
    for line, x, y in zip(lines, xs, y_coords):
        commands.extend([
            TextMatrix(translate(x, y)),
            Text(line),
        ])
    return commands


def _get_vertical_coordinates(
    lines,
    y1,
    y2,
    font_size,
    line_spacing,
    baseline,
):
    """Calculate vertical coordinates for all the lines at once, honoring the
    text baseline property.
    """
    line_spacing = font_size * line_spacing
    if baseline == 'top':
        first_y = y2 - line_spacing
    elif baseline == 'middle':
        midpoint = (y2 + y1) / 2.0
        # For the first line of vertically centered text, go up half the # of
        # lines, then go back down half the font size.
        first_y = midpoint - \
            (line_spacing - font_size) + \
            (((len(lines) - 1) / 2.0) * line_spacing)
    else:  # bottom
        first_y = y1 + \
            (line_spacing - font_size) + \
            (line_spacing * (len(lines) - 1))
    return [first_y - (i * line_spacing) for i in range(len(lines))]


def _get_horizontal_coordinates(lines, x1, x2, measure, align):
    # NOTE: this padding is to keep text annotations as they are from cutting
    # off text at the edges in certain conditions. The annotation rectangle
    # and how PDFs draw text needs to be revisited, as this padding shouldn't
    # be necessary.
    PADDING = 1
    if align == 'left':
        return [x1 + PADDING for _ in range(len(lines))]
    elif align == 'center':
        widths = [measure(line) for line in lines]
        max_width = x2 - x1
        return [x1 + ((max_width - width) / 2.0) - PADDING for width in widths]
    else:  # right
        widths = [measure(line) for line in lines]
        max_width = x2 - x1
        return [x1 + (max_width - width) - PADDING for width in widths]
