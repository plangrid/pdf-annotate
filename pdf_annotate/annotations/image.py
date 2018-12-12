# -*- coding: utf-8 -*-
import sys
import zlib

from pdfrw import PdfDict
from pdfrw import PdfName
from PIL import Image as PILImage
from PIL.ImageFile import ImageFile

from pdf_annotate.annotations.rect import RectAnnotation
from pdf_annotate.config.appearance import set_appearance_state
from pdf_annotate.graphics import ContentStream
from pdf_annotate.graphics import CTM
from pdf_annotate.graphics import Rect
from pdf_annotate.graphics import Restore
from pdf_annotate.graphics import Save
from pdf_annotate.graphics import XObject
from pdf_annotate.util.geometry import matrix_multiply
from pdf_annotate.util.geometry import scale
from pdf_annotate.util.geometry import translate


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

    def add_additional_resources(self, resources):
        resources.XObject = PdfDict(Image=self.image_xobject)

    def add_additional_pdf_object_data(self, obj):
        obj.Image = self.image_xobject

    @property
    def image_xobject(self):
        if self._image_xobject is None:
            self._image_xobject = self.make_image_xobject(
                self._appearance.image,
            )
        return self._image_xobject

    @staticmethod
    def make_image_xobject(image):
        """Construct a PdfDict representing the Image XObject, for inserting
        into the AP Resources dict.

        :param str|ImageFile image: Either a str representing the path to the
            image filename, or a PIL.ImageFile.ImageFile object representing
            the image loaded using the PIL library.
        :returns PdfDict: Image XObject
        """
        image = Image.resolve_image(image)
        width, height = image.size

        if image.mode == 'RGBA':
            # TODO this drops the alpha channel. PDF has its own transparency
            # model that we'll have to understand eventually.
            image = image.convert('RGB')

        xobj = PdfDict(
            stream=Image.make_image_content(image),
            BitsPerComponent=8,
            Filter=PdfName('FlateDecode'),  # TODO use a predictor
            ColorSpace=Image._get_color_space_name(image),
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

    @staticmethod
    def get_ctm(x1, y1, x2, y2):
        """Get the scaled and translated CTM for an image to be placed in the
        bounding box defined by [x1, y1, x2, y2].
        """
        return matrix_multiply(
            translate(x1, y1),
            scale(x2 - x1, y2 - y1),
        )

    def make_appearance_stream(self):
        A = self._appearance
        L = self._location

        stream = ContentStream([Save()])
        set_appearance_state(stream, A)
        stream.extend([
            Rect(L.x1, L.y1, L.x2 - L.x1, L.y2 - L.y1),
            CTM(self.get_ctm(L.x1, L.y1, L.x2, L.y2)),
            XObject('Image'),
            Restore(),
        ])
        return stream
