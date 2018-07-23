from six import StringIO

from pdf_annotate.annotations import Annotation
from pdf_annotate.annotations import make_border_dict
from pdf_annotate.graphics import restore
from pdf_annotate.graphics import save
from pdf_annotate.graphics import set_appearance_state
from pdf_annotate.graphics import stroke_or_fill


class FreeText(Annotation):
    subtype = 'FreeText'
    font = 'F1'

    @staticmethod
    def rotate(location, rotate, page_size):
        # TODO
        return location

    @staticmethod
    def scale(location, scale):
        # TODO
        return location

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
        return obj

    def graphics_commands(self):
        A = self._appearance
        L = self._location

        stream = StringIO()
        save(stream)

        set_appearance_state(stream, A)
        stream.write('BT ')
        # set font
        stream.write('/{} {} Tf '.format(self.font, A.font_size))
        stream.write('{} {} Td '.format(L.x1, L.y1))
        stream.write('({}) Tj '.format(A.text))

        stream.write('ET ')
        restore(stream)
        return stream.getvalue()
