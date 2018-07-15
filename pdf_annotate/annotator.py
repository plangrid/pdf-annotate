"""
Tool for adding annotations to PDF documents. Like, real PDF annotations, not
just additional shapes/whatever burned into the PDF content stream.
"""
from collections import namedtuple
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


# TODO this is super unclear how these are used
class Location(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


Appearance = namedtuple('Appearance', (
    'width',
    'height',
    'stroke_color',
    'stroke_width',
    'border_style',
    'dash_array',
    'fill',
))
