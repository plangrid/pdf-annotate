# -*- coding: utf-8 -*-
from pdfrw.objects import PdfDict
from pdfrw.objects import PdfName

from pdf_annotate.metadata import serialize_value


ALL_VERSIONS = ('1.3', '1.4', '1.5', '1.6', '1.7')


class Annotation(object):
    """Base class for all PDF annotation objects.

    Concrete annotations should define the following:
        * subtype (e.g. "Square")
        * make_rect() (bounding box of annotation)
        * get_matrix() (matrix entry of AP XObject)
        * add_additional_pdf_object_data [optional] additional entries to go
          in the PDF object
        * add_additional_resources [optional] additional entries to go in the
          Resources sub-dict of the annotation

    There is a lot of nuance and viewer-specific (mostly Acrobat and Bluebeam)
    details to consider when creating PDF annotations. One big thing that's not
    immediately clear from the PDF spec is that wherever possible, we fill in
    the annotations' type-specific details (e.g. BE and IC for squares), but
    also create and include an Appearance Stream. The latter gives us control
    over exactly how the annotation appears across different viewers, while the
    former allows Acrobat or BB to regenerate the appearance stream during
    editing.
    """
    versions = ALL_VERSIONS

    def __init__(self, location, appearance, metadata=None, rotation=0):
        """
        :param Location location:
        :param Appearance appearance:
        :param Metadata metadata:
        :param int rotation: text annotation cares about page orientation when
            building the graphics stream for the text content.
        """
        self._location = location
        self._appearance = appearance
        self._metadata = metadata
        self._rotation = rotation

    def as_pdf_object(self):
        """Return the PdfDict object representing the annotation.

        This is the function that a PdfAnnotator calls to generate the core
        PDF object that gets inserted into the PDF.
        """
        annotation_bbox = self.make_rect()
        appearance_stream = self._make_appearance_stream_dict()

        obj = PdfDict(
            Type=PdfName('Annot'),
            Subtype=PdfName(self.subtype),
            Rect=annotation_bbox,
            AP=appearance_stream,
        )

        self._add_metadata(obj, self._metadata)
        self.add_additional_pdf_object_data(obj)
        obj.indirect = True

        return obj

    @property
    def page(self):
        return self._location.page

    def validate(self, pdf_version):
        """Validate a new annotation against a given PDF version."""
        pass

    def _add_metadata(self, obj, metadata):
        if metadata is None:
            return
        for name, value in metadata.iter():
            obj[PdfName(name)] = serialize_value(value)

    def _make_ap_resources(self):
        """Make the Resources entry for the appearance stream dictionary.

        Implement add_additional_resources to add additional entries -
        fonts, XObjects, graphics state - to the Resources dictionary.
        """
        resources = PdfDict(ProcSet=PdfName('PDF'))
        self.add_additional_resources(resources)
        return resources

    def _make_appearance_stream_dict(self):
        resources = self._make_ap_resources()

        appearance_stream = self._appearance.appearance_stream
        if appearance_stream is None:
            appearance_stream = self.graphics_commands()

        normal_appearance = PdfDict(
            stream=appearance_stream,
            BBox=self.make_rect(),
            Resources=resources,
            Matrix=self.get_matrix(),
            Type=PdfName('XObject'),
            Subtype=PdfName('Form'),
            FormType=1,
        )
        return PdfDict(**{'N': normal_appearance})

    def add_additional_pdf_object_data(self, obj):
        """Add additional keys to the PDF object. Default is a no-op.

        :param PdfDict obj: the PDF object to be inserted into the PDF
        """
        pass

    def add_additional_resources(self, resources):
        """Add additional keys to the Resources PDF dictionary. Default is a
        no-op.

        :param PdfDict resources: Resources PDF dictionary
        """
        pass

    def get_matrix(self):
        """Get the appearance stream's Matrix entry."""
        raise NotImplementedError()

    def make_rect(self):
        """Return a bounding box that encompasses the entire annotation."""
        raise NotImplementedError()


def make_border_dict(appearance):
    A = appearance
    return _make_border_dict(A.stroke_width, A.border_style, A.dash_array)


def _make_border_dict(width, style, dash_array=None):
    border = PdfDict(
        Type=PdfName('Border'),
        W=width,
        S=PdfName(style),
    )
    if dash_array:
        if style != 'D':
            raise ValueError('Dash array only applies to dashed borders!')
        border.D = dash_array
    return border


class Stamp(object):
    subtype = 'Stamp'
