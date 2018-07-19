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
from pdf_annotate.appearance import Appearance
from pdf_annotate.location import Location
from pdf_annotate.utils import normalize_rotation


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

    def get_rotation(self, page_number):
        """Returns the rotation of a specified page."""
        page = self.get_page(page_number)
        # TODO need to check parent since Rotate is inheritable
        rotate = int(page.Rotate or 0)
        return normalize_rotation(rotate)


class PdfAnnotator(object):

    def __init__(self, filename, draw_on_rotated_pages=True):
        self._filename = filename
        self._pdf = PDF(filename)
        self._draw_on_rotated_pages = draw_on_rotated_pages

    def get_size(self, page_number):
        """Returns the size of the specified page's MediaBox."""
        page = self._pdf.get_page(page_number)
        x1, y1, x2, y2 = map(float, page.MediaBox)
        rotation = self._pdf.get_rotation(page_number)

        if not self._draw_on_rotated_pages or rotation in (0, 180):
            return (x2 - x1, y2 - y1)

        return (y2 - y1, x2 - x1)

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
        # Rotate all elements of the location so we can act like we're drawing
        # on the page in a viewer.
        if self._draw_on_rotated_pages:
            location = annotation_cls.rotate(
                location,
                self._pdf.get_rotation(location.page),
                self.get_size(location.page),
            )
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
