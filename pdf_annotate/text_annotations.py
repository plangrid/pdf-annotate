# -*- coding: utf-8 -*-
"""
FreeText annotation.
"""
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
from pdf_annotate.utils import rotate
from pdf_annotate.utils import translate


class FreeText(Annotation):
    """FreeText annotation. Right now, we only support writing text in the
    Helvetica font. Dealing with fonts is tricky business, so we'll leave that
    for later.
    """
    subtype = 'FreeText'
    font = 'PDFANNOTATORFONT1'

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
            TextMatrix(self._get_text_matrix()),
            Text(A.text),
            EndText(),
            Restore(),
        ])

        return stream.resolve()

    def _get_text_matrix(self):
        A = self._appearance
        L = self._location
        # Not entirely sure what y offsets I should be calculating here.
        if self._rotation == 0:
            return translate(L.x1 + 1, L.y2 - A.font_size)
        elif self._rotation == 90:
            return translate(L.y1 + 1, -(L.x1 + A.font_size))
        elif self._rotation == 180:
            return translate(-L.x2 + 1, -(L.y1 + A.font_size))
        else:  # 270
            return translate(-L.y2 + 1, L.x2 - A.font_size)

    def _get_graphics_cm(self):
        return rotate(self._rotation)
