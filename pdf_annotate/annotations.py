# -*- coding: utf-8 -*-
from pdfrw.objects import PdfDict, PdfName
from six import StringIO

from pdf_annotate.appearance import Appearance


ALL_VERSIONS = ('1.3', '1.4', '1.5', '1.6', '1.7')

PRINT_FLAG = 4


class Annotation(object):
    """Base class for all PDF annotation objects.

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

    def __init__(self, location, appearance, metadata=None):
        self._location = location
        self._appearance = appearance

    @property
    def page(self):
        return self._location.page

    def validate(self, pdf_version):
        """Validate a new annotation against a given PDF version."""
        pass

    def make_base_object(self):
        """Create the base PDF object with properties that all annotations
        share.
        """
        # TODO add metadata
        return PdfDict(
            **{
                'Type': PdfName('Annot'),
                'Subtype': PdfName(self.subtype),
                'Rect': self.make_rect(),
                # TODO support passing in flags
                'F': PRINT_FLAG,
            }
        )

    def make_ap_dict(self):
        return PdfDict(**{'N': self.make_n_dict()})

    def get_matrix(self):
        raise NotImplementedError()

    def make_n_dict(self):
        return PdfDict(
            stream=self.graphics_commands(),
            **{
                'BBox': self.make_rect(),
                'Resources': PdfDict(**{'ProcSet': PdfName('PDF')}),
                'Matrix': self.get_matrix(),
                'Type': PdfName('XObject'),
                'Subtype': PdfName('Form'),
                'FormType': 1,
            }
        )

    def make_rect(self):
        """Return a bounding box that encompasses the entire annotation."""
        raise NotImplementedError()

    def as_pdf_object(self):
        """Return the PdfDict object representing the annotation."""
        raise NotImplementedError()


def make_border_dict(appearance):
    border = PdfDict(
        **{
            'Type': PdfName('Border'),
            'W': appearance.stroke_width,
            'S': PdfName(appearance.border_style),
        }
    )
    if appearance.dash_array:
        if appearance.border_style != 'D':
            raise ValueError('Dash array only applies to dashed borders!')
        border.D = appearance.dash_array
    return border


def set_appearance_state(stream, A):
    """Update the graphics command stream to reflect appearance properties.

    :param StringIO stream: current string of graphics state
    :param Appearance A: appearance object
    """
    stream.write('{} {} {} RG '.format(*A.stroke_color))
    stream.write('{} w '.format(A.stroke_width))
    # TODO support more color spaces - CMYK and GrayScale
    if A.fill is not Appearance.TRANSPARENT and A.fill is not None:
        stream.write('{} {} {} rg '.format(*A.fill))


def stroke(stream):
    stream.write('S ')


def stroke_or_fill(stream, A):
    if A.fill is not Appearance.TRANSPARENT and A.fill is not None:
        stream.write('B ')
    else:
        stroke(stream)


class FreeText(object):
    subtype = 'FreeText'


class Stamp(object):
    subtype = 'Stamp'
