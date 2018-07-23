from six import StringIO

from pdf_annotate.annotations import Annotation
from pdf_annotate.annotations import make_border_dict
from pdf_annotate.annotations import restore
from pdf_annotate.annotations import save
from pdf_annotate.annotations import set_appearance_state
from pdf_annotate.annotations import stroke_or_fill


class FreeText(Annotation):
    subtype = 'FreeText'

    @staticmethod
    def rotate(location, rotate, page_size):
        pass

    @staticmethod
    def scale(location, scale):
        pass

    def get_matrix(self):
        pass

    def make_rect(self):
        pass

    def as_pdf_object(self):
        obj = self.make_base_object()

    def graphics_commands(self):
        A = self._appearance

        stream = StringIO()
        save(stream)

        set_appearance_state(stream, A)
        stream.write('BT ')
        # set font
        stream.write('/{} {} Tf '.format('Helv', A.font_size))

        stream.write('ET ')
        restore(stream)
        return stream.getvalue()
