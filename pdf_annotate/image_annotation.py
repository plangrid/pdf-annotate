# -*- coding: utf-8 -*-
import sys
import zlib

from pdfrw import PdfDict
from pdfrw import PdfName
from PIL import Image as PILImage
from PIL.ImageFile import ImageFile

from pdf_annotate.graphics import ContentStream
from pdf_annotate.graphics import CTM
from pdf_annotate.graphics import Rect
from pdf_annotate.graphics import Restore
from pdf_annotate.graphics import Save
from pdf_annotate.graphics import set_appearance_state
from pdf_annotate.graphics import XObject
from pdf_annotate.rect_annotations import RectAnnotation
from pdf_annotate.utils import matrix_multiply
from pdf_annotate.utils import rotate
from pdf_annotate.utils import scale
from pdf_annotate.utils import translate


class Image(RectAnnotation):
    """A basic Image annotation class.

    There is no native image annotation in the PDF spec, but image annotations
    can be easily approximated by drawing an Image XObject in the appearance
    stream.

    This implementation relies on the python Pillow library to retrieve the
    image's raw sample data, then formats that data as expected by the PDF
    spec.

    Additional work needs to be done. For example:
        - supporting transparency
        - better compression (e.g. using a Predictor value for FlateDecode)
        - support for other image types. For example I think the PDF spec has
          some limited support for just including JPEGs directly.
        - more color spaces - Pillow lists a ton of potential image modes.
    """

    subtype = 'Square'
    _image_xobject = None  # PdfDict of Image XObject

    def make_ap_resources(self):
        resources = super(Image, self).make_ap_resources()
        resources['XObject'] = PdfDict(Image=self.image_xobject)
        return resources

    @property
    def image_xobject(self):
        if self._image_xobject is None:
            self._image_xobject = self.make_image_xobject()
        return self._image_xobject

    def make_image_xobject(self):
        image = self.resolve_image(self._appearance.image)
        width, height = image.size

        if image.mode == 'RGBA':
            # TODO this drops the alpha channel. PDF has its own transparency
            # model that we'll have to understand eventually.
            image = image.convert('RGB')

        xobj = PdfDict(
            stream=self.make_image_content(image),
            BitsPerComponent=8,
            Filter=PdfName('FlateDecode'),  # TODO use a predictor
            ColorSpace=self._get_color_space_name(image),
            Width=width,
            Height=height,
            Subtype=PdfName('Image'),
            Type=PdfName('XObject'),
        )
        return xobj

    @staticmethod
    def resolve_image(image_or_filename):
        if isinstance(image_or_filename, str):
            return PILImage.open(image_or_filename)
        elif isinstance(image_or_filename, ImageFile):
            return image_or_filename
        raise ValueError('Invalid image format: {}'.format(
            image_or_filename.__class__.__name__))

    @staticmethod
    def _get_color_space_name(image):
        if image.mode == 'RGB':
            return PdfName('DeviceRGB')
        elif image.mode in ('L', '1'):
            return PdfName('DeviceGray')
        raise ValueError('Image color space not yet supported')

    @staticmethod
    def make_image_content(image):
        compressed = zlib.compress(Image.get_raw_image_bytes(image))
        if sys.version_info.major < 3:
            return compressed
        # Right now, pdfrw needs strings, not bytes like you'd expect in py3,
        # for binary stream objects. This might change in future versions.
        return compressed.decode('Latin-1')

    @staticmethod
    def get_raw_image_bytes(image):
        if image.mode in ('L', '1'):
            # If this is grayscale or single-channel, we can avoid dealing with
            # the nested tuples in multi-channel images. This bytes/bytearray
            # wrapped approach is the only way that works in both py2 and py3.
            return bytes(bytearray(image.getdata()))

        elif image.mode == 'RGB':
            raw_image_data = list(image.getdata())
            array = bytearray()
            for rgb in raw_image_data:
                array.extend(rgb)
            return bytes(array)

        raise ValueError('Image color space not yet supported')

    def as_pdf_object(self):
        obj = super(Image, self).as_pdf_object()
        obj.Image = self.image_xobject
        return obj

    def graphics_commands(self):
        A = self._appearance
        L = self._location

        stream = ContentStream()
        set_appearance_state(stream, A)
        stream.extend([
            Rect(L.x1, L.y1, L.x2 - L.x1, L.y2 - L.y1),
            Save(),
            CTM(self._get_ctm()),
            XObject('Image'),
            Restore(),
        ])
        return stream.resolve()

    def _get_ctm(self):
        # Scale the image and place it on the page
        L = self._location
        width = L.x2 - L.x1
        height = L.y2 - L.y1
        if self._rotation == 0:
            placement = translate(L.x1, L.y1)
        elif self._rotation == 90:
            placement = translate(L.x2, L.y1)
        elif self._rotation == 180:
            placement = translate(L.x2, L.y2)
        else:  # 270
            placement = translate(L.x1, L.y2)

        return matrix_multiply(
            placement,
            scale(width, height),
            rotate(self._rotation),
        )
