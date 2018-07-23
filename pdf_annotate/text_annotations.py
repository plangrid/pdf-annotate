from six import StringIO

from pdf_annotate.annotations import Annotation
from pdf_annotate.annotations import _make_border_dict
from pdf_annotate.graphics import restore
from pdf_annotate.graphics import save
from pdf_annotate.graphics import set_appearance_state
from pdf_annotate.graphics import stroke_or_fill
from pdf_annotate.rect_annotations import RectAnnotation


class FreeText(Annotation):
    subtype = 'FreeText'
    font = 'PDFANNOTATORFONT1'

    @staticmethod
    def rotate(location, rotate, page_size):
        # TODO this works for locating the text box, but it draws the text
        # rotated the same rotation as the page.
        return RectAnnotation.rotate(location, rotate, page_size)

    @staticmethod
    def scale(location, scale):
        return RectAnnotation.scale(location, rotate, page_size)

    def get_matrix(self):
        L = self._location
        return [1, 0, 0, 1, -L.x1, -L.y1]

    def make_rect(self):
        L = self._location
        return [L.x1, L.y1, L.x2, L.y2]

    def make_default_appearance(self):
        A = self._appearance
        color_str = '{} {} {}'.format(*A.stroke_color)
        font_str = '{} {}'.format(self.font, A.font_size)
        return '{} rg {} Tf'.format(color_str, font_str)

    def as_pdf_object(self):
        obj = self.make_base_object()
        obj.AP = self.make_ap_dict()
        obj.Contents = self._appearance.text
        obj.DA = self.make_default_appearance()
        A = self._appearance
        # TODO allow setting border on free text boxes
        obj.BS = _make_border_dict(width=0, style='S')
        # TODO DS and RC seem to be filled in by Acrobat and Bluebeam
        return obj

    def graphics_commands(self):
        A = self._appearance
        L = self._location

        stream = StringIO()
        save(stream)

        stream.write('BT ')
        stream.write('{} {} {} rg '.format(*A.stroke_color))
        stream.write('/{} {} Tf '.format(self.font, A.font_size))
        stream.write('{} {} Td '.format(L.x1 + 1, L.y2 - A.font_size))
        stream.write('({}) Tj '.format(A.text))
        stream.write('ET ')

        restore(stream)
        return stream.getvalue()
