"""
Tool for adding annotations to PDF documents. Like, real PDF annotations, not
just additional shapes/whatever burned into the PDF content stream.
"""
from collections import namedtuple
from pdfrw import PdfReader, PdfWriter
from pdfrw.objects import PdfDict, PdfName


class PDF(object):
    def __init__(self, filename):
        self._reader = PdfReader(filename)

    def get_page(self, page_number):
        # TODO this won't always work b/c of how PDFs can have page trees
        return self._reader.Root.Pages.Kids[page_number]


class PdfAnnotator(object):

    def __init__(self, filename):
        self._filename = filename
        self._pdf = PDF(filename)

    def add_annotation(
        self,
        annotation_type,
        location,
        appearance,
        metadata=None,
    ):
        """Add an annotation of the given type, with the given parameters, to
        the given location of the PDF.

        :param str annotation_type:
        :param Location location:
        :param Appearance appearance:
        :param Metadata metadata:
        """
        # TODO filter on valid types
        # TODO filter on valid PDF versions, by type
        if annotation_type == 'square':
            annotation = Square(location, appearance, metadata)

        self._add_annotation(annotation)

    def _add_annotation(self, annotation):
        # Add PDF object to page tree
        page = self._pdf.get_page(annotation.page)
        if page.Annots:
            page.Annots.append(annotation.as_pdf_object())
        else:
            page.Annots = [annotation.as_pdf_object()]

    def write(self, filename=None, overwrite=False):
        if filename is None and not overwrite:
            raise ValueError(
                'Must specify either output filename or overwrite flag'
            )
        if overwrite:
            filename = self._filename

        writer = PdfWriter()
        writer.write(fname=filename, trailer=self._pdf._reader)


Location = namedtuple('Location', ('x', 'y', 'page'))
Appearance = namedtuple('Appearance', ('width', 'height', 'color'))


class Square(object):
    def __init__(self, location, appearance, *args, **kwargs):
        self._location = location
        self._appearance = appearance

    @property
    def page(self):
        return self._location.page

    def _make_rect(self):
        """Returns the bounding box of the annotation in PDF default user space
        units.
        """
        return [
            self._location.x,
            self._location.y,
            self._location.x + self._appearance.width,
            self._location.y + self._appearance.height,
        ]

    def _make_ap_stream(self):
        return (
            '{color} RG '
            '5 w '
            '0 0 {width} {height} re '
            'S'
        ).format(
            color=self._appearance.color,
            width=self._appearance.width,
            height=self._appearance.height,
        )

    def _make_ap(self):
        """Make PDF annotation appearance dictionary."""
        return PdfDict(
            stream=self._make_ap_stream(),
            **{
                'BBox': [
                    0,
                    0,
                    self._appearance.width,
                    self._appearance.height
                ],
                'FormType': 1,
                'Matrix': [1, 0, 0, 1, 0, 0],
                'Resources': PdfDict({
                    PdfName('ProcSet'): [PdfName('PDF')],
                }),
                'Subtype': PdfName('Form'),
                'Type': PdfName('XObject'),
            }
        )

    def as_pdf_object(self):
        return PdfDict(
            **{
                'AP': PdfDict({PdfName('N'): self._make_ap()}),
                'Rect': self._make_rect(),
                'Type': PdfName('Annot'),
                'Subtype': PdfName('Square'),
            }
        )
