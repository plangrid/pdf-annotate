# -*- coding: utf-8 -*-
"""
Tool for adding annotations to PDF documents. Like, real PDF annotations, not
just additional shapes/whatever burned into the PDF content stream.
"""
from pdfrw import PdfReader, PdfWriter
from pdfrw.objects import PdfDict, PdfName

from pdf_annotate.points_annotations import Line
from pdf_annotate.points_annotations import Polygon
from pdf_annotate.points_annotations import Polyline
from pdf_annotate.rect_annotations import Circle
from pdf_annotate.rect_annotations import Square
from pdf_annotate.appearance import Appearance
from pdf_annotate.location import Location
from pdf_annotate.utils import is_numeric
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

    def __init__(
        self,
        filename,
        draw_on_rotated_pages=True,
        scale=None,
        rastered_dimensions=None,
    ):
        """Draw annotations directly on PDFs.

        :param str filename: file of PDF to read in
        :param bool draw_on_rotated_pages: if True (the default), draw on the
            PDF as if drawn in a viewing application. E.g. (0,0) in user space
            on a PDF rotated 90° is (0,width) on the rotated PDF. Cannot be
            False if rastered_dimensions is specified.
        :param number|tuple|None scale: number by which to scale all coordinates
            to get to default user space. Use this if, for example, your points
            in the coordinate space of the PDF viewed at a dpi. In this case,
            scale would be 72/dpi. Can also specify a 2-tuple of x and y scale.
        """
        self._filename = filename
        self._pdf = PDF(filename)
        self._scale = self._expand_scale(scale)
        self._draw_on_rotated_pages = draw_on_rotated_pages
        self._dimensions = {}

    def _expand_scale(self, scale):
        if is_numeric(scale):
            return (scale, scale)
        return scale

    def set_page_dimensions(self, dimensions, page_number):
        """Set dimensions for a given page number. If set, the dimensions for
        this page override the document-wide rotation and scale settings.

        :param tuple|None dimensions: As a convenient alternative to scale and
            draw_on_rotated_pages, you can pass in the dimensions of your
            sheet when viewed in a certain setting. For example, an 8.5"x11" PDF,
            rotated at 90° and rastered at 150 dpi, would produce dimensions of
            (1650, 1275). If you pass this in, you can then specify your
            coordinates in this coordinate space.
        :param int page_number:
        """
        self._dimensions[page_number] = dimensions

    def get_size(self, page_number):
        """Returns the size of the specified page's MediaBox (pts)."""
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

        scale, rotate = self._get_scale_rotate(location.page)
        if scale is not None:
            location = annotation_cls.scale(location, scale)

        if rotate:
            location = annotation_cls.rotate(
                location,
                self._pdf.get_rotation(location.page),
                self.get_size(location.page),
            )

        annotation = annotation_cls(location, appearance, metadata)
        annotation.validate(self._pdf.pdf_version)
        self._add_annotation(annotation)

    def _get_scale_rotate(self, page_number):
        """Get scale for the given page. Always returns None or a 2-tuple."""
        dimensions = self._dimensions.get(page_number)
        if dimensions is not None:
            width_d, height_d = dimensions
            width_pts, height_pts = self.get_size(page_number)
            rotation = self._pdf.get_rotation(page_number)
            # get_size already accounts for rotation
            return (width_pts / width_d, height_pts / height_d), True

        return self._scale, self._draw_on_rotated_pages

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
