"""
Tool for adding annotations to PDF documents. Like, real PDF annotations, not
just additional shapes/whatever burned into the PDF content stream.
"""
from pdfrw import PdfReader, PdfWriter
from pdfrw.objects import PdfDict, PdfName

from pdf_annotate.annotations import (
    Circle,
    Line,
    Polygon,
    Polyline,
    Square,
)


NAME_TO_ANNOTATION = {
    'square': Square,
    'circle': Circle,
    'line': Line,
    'polygon': Polygon,
    'polyline': Polyline,
}


class PDF(object):
    def __init__(self, filename):
        self._reader = PdfReader(filename)
        self.pdf_version = self._reader.private.pdfdict.version

    def get_page(self, page_number):
        if page_number > len(self._reader.pages) - 1:
            raise ValueError('Page number {} out of bounds ({} pages)'.format(
                page_number,
                len(self._reader.pages),
            ))
        return self._reader.pages[page_number]


class PdfAnnotator(object):

    def __init__(self, filename):
        self._filename = filename
        self._pdf = PDF(filename)

    def get_size(self, page_number):
        """Returns the size of the specified page's MediaBox."""
        page = self._pdf.get_page(page_number)
        # TODO Might need to check the parent, since MediaBox is inheritable
        x1, y1, x2, y2 = map(float, page.MediaBox)
        return (x2 - x1, y2 - y1)

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
        # TODO filter on valid PDF versions, by type
        # TODO allow more fine grained control by allowing specification of AP
        # dictionary that overrides other attributes.
        annotation_cls = NAME_TO_ANNOTATION.get(annotation_type)
        if annotation_cls is None:
            raise ValueError('Invalid/unsupported annotation type: {}'.format(
                annotation_type
            ))
        annotation = annotation_cls(location, appearance, metadata)
        annotation.validate(self._pdf.pdf_version)
        self._add_annotation(annotation)

    def _add_annotation(self, annotation):
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

        writer = PdfWriter(version=self._pdf.pdf_version)
        writer.write(fname=filename, trailer=self._pdf._reader)


# TODO this is super unclear how these are used
class Location(object):
    def __init__(self, **kwargs):
        if 'page' not in kwargs:
            raise ValueError('Must set page on annotations')
        for k, v in kwargs.items():
            setattr(self, k, v)


class Appearance(object):
    BLACK = (0, 0, 0)
    TRANSPARENT = tuple()

    def __init__(self, **kwargs):
        self.stroke_color = kwargs.get('stroke_color', self.BLACK)
        self.stroke_width = kwargs.get('stroke_width', 1)
        self.border_style = kwargs.get('border_style', 'S')
        self.fill = kwargs.get('fill', self.TRANSPARENT)
        self.dash_array = kwargs.get('dash_array', None)

        for k, v in kwargs.items():
            setattr(self, k, v)
