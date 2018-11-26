# -*- coding: utf-8 -*-
import attr

from pdf_annotate.config.constants import ALLOWED_ALIGNS
from pdf_annotate.config.constants import ALLOWED_BASELINES
from pdf_annotate.config.constants import ALLOWED_LINE_CAPS
from pdf_annotate.config.constants import ALLOWED_LINE_JOINS
from pdf_annotate.config.constants import BLACK
from pdf_annotate.config.constants import DEFAULT_BORDER_STYLE
from pdf_annotate.config.constants import DEFAULT_CONTENT
from pdf_annotate.config.constants import DEFAULT_FONT_SIZE
from pdf_annotate.config.constants import DEFAULT_LINE_SPACING
from pdf_annotate.config.constants import DEFAULT_STROKE_WIDTH
from pdf_annotate.config.constants import TEXT_ALIGN_LEFT
from pdf_annotate.config.constants import TEXT_BASELINE_MIDDLE
from pdf_annotate.graphics import ContentStream
from pdf_annotate.util.validation import between
from pdf_annotate.util.validation import Boolean
from pdf_annotate.util.validation import Color
from pdf_annotate.util.validation import Enum
from pdf_annotate.util.validation import Field
from pdf_annotate.util.validation import Number
from pdf_annotate.util.validation import positive
from pdf_annotate.util.validation import String


@attr.s
class Appearance(object):
    # Stroke attributes
    stroke_color = Color(default=BLACK)
    stroke_width = Number(default=DEFAULT_STROKE_WIDTH, validator=positive)
    border_style = String(default=DEFAULT_BORDER_STYLE)
    dash_array = String(default=None)
    line_cap = Enum(ALLOWED_LINE_CAPS, default=None)
    line_join = Enum(ALLOWED_LINE_JOINS, default=None)
    miter_limit = Number(default=None, validator=positive)
    stroke_transparency = Number(default=None, validator=between(0, 1))

    # Fill attributes
    fill = Color(default=None)
    fill_transparency = Number(default=None, validator=between(0, 1))

    # Text attributes
    content = String(default=DEFAULT_CONTENT)
    font_size = Number(default=DEFAULT_FONT_SIZE, validator=positive)
    text_align = Enum(ALLOWED_ALIGNS, default=TEXT_ALIGN_LEFT)
    text_baseline = Enum(ALLOWED_BASELINES, default=TEXT_BASELINE_MIDDLE)
    line_spacing = Number(default=DEFAULT_LINE_SPACING, validator=positive)
    wrap_text = Boolean(default=True)

    # Image attributes
    image = String(default=None)

    # Advanced attributes
    appearance_stream = Field(ContentStream, default=None)
    xobjects = Field(dict, default=None)
    graphics_states = Field(dict, default=None)

    def copy(self, **kwargs):
        A = Appearance(**kwargs)
        for k, v in self.__dict__.items():
            if k not in kwargs:
                setattr(A, k, v)
        return A
