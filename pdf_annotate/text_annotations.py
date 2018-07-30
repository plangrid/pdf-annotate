from six import StringIO

from pdf_annotate.annotations import Annotation
from pdf_annotate.annotations import _make_border_dict
from pdf_annotate.graphics import restore
from pdf_annotate.graphics import save
from pdf_annotate.graphics import set_appearance_state
from pdf_annotate.graphics import set_cm
from pdf_annotate.graphics import set_tm
from pdf_annotate.graphics import stroke_or_fill
from pdf_annotate.rect_annotations import RectAnnotation
from pdf_annotate.utils import identity
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
        color_str = '{} {} {}'.format(*A.stroke_color)
        font_str = '/{} {}'.format(self.font, A.font_size)
        return '{} rg {} Tf'.format(color_str, font_str)

    def as_pdf_object(self):
        obj = self.make_base_object()
        obj.AP = self.make_ap_dict()
        obj.Contents = self._appearance.text
        obj.DA = self.make_default_appearance()
        obj.C = []
        A = self._appearance
        # TODO allow setting border on free text boxes
        obj.BS = _make_border_dict(width=0, style='S')
        # TODO DS is required to have BB not redraw the annotation in their own
        # style when you edit it.
        return obj

    def graphics_commands(self):
        A = self._appearance
        L = self._location

        stream = StringIO()
        save(stream)

        set_cm(stream, self._get_graphics_cm())
        # Not quite sure why we write black + the stroke color before BT as well
        stream.write('1 1 1 rg ')
        stream.write('{} {} {} RG '.format(*A.stroke_color))
        stream.write('0 w ')

        stream.write('BT ')
        stream.write('{} {} {} rg '.format(*A.stroke_color))
        stream.write('/{} {} Tf '.format(self.font, A.font_size))
        # TODO will have to deal with writing multiple lines. Probably will
        # have to understand the XObject -> Rect mapping in this case.
        set_tm(stream, self._get_text_matrix())
        stream.write('({}) Tj '.format(A.text))
        stream.write('ET ')

        restore(stream)
        return stream.getvalue()

    def _get_text_matrix(self):
        L = self._location
        A = self._appearance
        # Not entirely sure what y offsets I should be calculating here.
        if L.rotation == 0:
            return translate(L.x1 + 1, L.y2 - A.font_size)
        elif L.rotation == 90:
            return translate(L.y1 + 1, -(L.x1 + A.font_size))
        elif L.rotation == 180:
            return translate(-L.x2 + 1, -(L.y1 + A.font_size))
        # 270
        else:
            return translate(-L.y2 + 1, L.x2 - A.font_size)

    def _get_graphics_cm(self):
        return rotate(self._location.rotation)
