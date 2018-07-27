# -*- coding: utf-8 -*-
"""
Tool for adding annotations to PDF documents. Like, real PDF annotations, not
just additional shapes/whatever burned into the PDF content stream.
"""
import warnings

from pdfrw import PdfReader, PdfWriter
from pdfrw.objects import PdfDict, PdfName

from pdf_annotate.points_annotations import Ink
from pdf_annotate.points_annotations import Line
from pdf_annotate.points_annotations import Polygon
from pdf_annotate.points_annotations import Polyline
from pdf_annotate.rect_annotations import Circle
from pdf_annotate.rect_annotations import Square
from pdf_annotate.text_annotations import FreeText
from pdf_annotate.appearance import Appearance
from pdf_annotate.location import Location
from pdf_annotate.utils import is_numeric
from pdf_annotate.utils import normalize_rotation
from pdf_annotate.utils import rotate
from pdf_annotate.utils import identity
from pdf_annotate.utils import scale
from pdf_annotate.utils import translate
from pdf_annotate.utils import matrix_multiply


NAME_TO_ANNOTATION = {
    'square': Square,
    'circle': Circle,
    'line': Line,
    'polygon': Polygon,
    'polyline': Polyline,
    'ink': Ink,
    'text': FreeText,
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
        rotate = int(page.inheritable.Rotate or 0)
        return normalize_rotation(rotate)


class PdfAnnotator(object):

    def __init__(self, filename, scale=None):
        """Draw annotations directly on PDFs. Annotations are always drawn on
        as if you're drawing them in a viewer, i.e. they take into account page
        rotation and weird, translated coordinate spaces.

        :param str filename: file of PDF to read in
        :param number|tuple|None scale: number by which to scale all coordinates
            to get to default user space. Use this if, for example, your points
            in the coordinate space of the PDF viewed at a dpi. In this case,
            scale would be 72/dpi. Can also specify a 2-tuple of x and y scale.
        """
        self._filename = filename
        self._pdf = PDF(filename)
        self._scale = self._expand_scale(scale)
        self._dimensions = {}

    def _expand_scale(self, scale):
        if scale is None:
            return 1, 1
        elif is_numeric(scale):
            return (scale, scale)
        return scale

    def set_page_dimensions(self, dimensions, page_number):
        """Set dimensions for a given page number. If set, the dimensions for
        this page override the document-wide rotation and scale settings.

        :param tuple|None dimensions: As a convenient alternative to scale and
            you can pass in the dimensions of your sheet when viewed in a
            certain setting. For example, an 8.5"x11" PDF, rotated at 90° and
            rastered at 150 dpi, would produce dimensions of (1650, 1275). If
            you pass this in, you can then specify your coordinates in this
            coordinate space.
        :param int page_number:
        """
        self._dimensions[page_number] = dimensions

    def get_mediabox(self, page_number):
        page = self._pdf.get_page(page_number)
        return list(map(float, page.inheritable.MediaBox))

    def get_size(self, page_number):
        """Returns the size of the specified page's MediaBox (pts), accounting
        for page rotation.

        :param int page_number:
        :returns tuple: If page is rotated 90° or 270°, the returned value will
            be (height, width) in PDF user space. Otherwise the returned value
            will be (width, height).
        """
        page = self._pdf.get_page(page_number)
        x1, y1, x2, y2 = map(float, page.inheritable.MediaBox)
        rotation = self._pdf.get_rotation(page_number)

        if rotation in (0, 180):
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
        self._before_add(location)
        annotation = self.get_annotation(
            annotation_type,
            location,
            appearance,
            metadata,
        )
        self._add_annotation(annotation)

    def _before_add(self, location):
        # Steps to take before trying to add an annotation to `location`
        page = self._pdf.get_page(location.page)
        user_unit = page.inheritable.UserUnit
        if user_unit not in (1, None):
            warnings.warn(
                'Unsupported UserUnit (value: {})'.format(user_unit)
            )

    def get_annotation(self, annotation_type, location, appearance, metadata):
        # TODO filter on valid PDF versions, by type
        # TODO allow more fine grained control by allowing specification of AP
        # dictionary that overrides other attributes.
        annotation_cls = NAME_TO_ANNOTATION.get(annotation_type)
        if annotation_cls is None:
            raise ValueError('Invalid/unsupported annotation type: {}'.format(
                annotation_type
            ))

        transform = self.get_transform(location.page)
        # We don't have to change anything if the transform is ideneity
        if transform != identity():
            location = annotation_cls.transform(location, transform)

        annotation = annotation_cls(location, appearance, metadata)
        annotation.validate(self._pdf.pdf_version)
        return annotation

    def get_transform(self, page_number):
        media_box = self.get_mediabox(page_number)
        rotation = self._pdf.get_rotation(page_number)
        dimensions = self._dimensions.get(page_number)
        return self._get_transform(media_box, rotation, dimensions, self._scale)

    @staticmethod
    def _get_transform(media_box, rotation, dimensions, _scale):
        """Get the transformation required to go from the user's desired
        coordinate space to PDF user space, taking into account rotation,
        scaling, translation (for things like weird media boxes).
        """
        # Unrotated width and height, in pts
        W = media_box[2] - media_box[0]
        H = media_box[3] - media_box[1]

        if dimensions is not None:
            # User-specified dimensions for a particular page just give us the
            # scaling factor to use for that page.
            width_d, height_d = dimensions
            width_pts, height_pts = W, H
            if rotation in (90, 270):
                width_pts, height_pts = H, W
            x_scale = (width_pts / width_d)
            y_scale = (height_pts / height_d)
        else:
            x_scale, y_scale = _scale

        scale_matrix = scale(x_scale, y_scale)

        # TODO this will take care of weird offset media boxes
        # x_translate = 0 - media_box[0]
        # y_translate = 0 - media_box[1]
        # translate_matrix = translate(x_translate, y_translate)

        # Because of how rotation the point isn't rotated around an axis, but
        # the axis itself shifts, we have to represent the rotation as a
        # rotation, then a translation.
        rotation_matrix = rotate(rotation)

        translate_matrix = identity()
        if rotation == 90:
            translate_matrix = translate(W, 0)
        elif rotation == 180:
            translate_matrix = translate(W, H)
        elif rotation == 270:
            translate_matrix = translate(0, H)

        transform = matrix_multiply(
            matrix_multiply(translate_matrix, rotation_matrix),
            scale_matrix,
        )
        return transform

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
