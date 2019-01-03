# -*- coding: utf-8 -*-
import sys
import zlib
from io import BytesIO

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

    Supported formats are PNG, JPEG, and GIF. Only the first frame from multi-
    frame GIFs is used.

    This implementation relies on the python Pillow library to retrieve the
    image's raw sample data, then formats that data as expected by the PDF
    spec.

    Additional work needs to be done. For example:
        - supporting the reading of transparency directly from RGBA images
        - better compression (e.g. using a Predictor value for FlateDecode)
        - supporting DeviceCMYK directly
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

        PNGs and GIFs are treated equally - the raw sample values are included
        using PDF's FlateDecode compression format. JPEGs can be included in
        their original form using the DCTDecode filter.

        Details about file formats and allowed modes can be found at
        https://pillow.readthedocs.io/en/5.3.x/handbook/image-file-formats.html

        :param str|ImageFile image: Either a str representing the path to the
            image filename, or a PIL.ImageFile.ImageFile object representing
            the image loaded using the PIL library.
        :returns PdfDict: Image XObject
        """
        image = Image.resolve_image(image)
        # PILImage.convert drops the format attribute
        image_format = image.format
        width, height = image.size

        if image_format in ('PNG', 'GIF') and image.mode in ('RGBA', 'P'):
            # Right now the alpha channel from RGBA images is dropped; we
            # should eventually incorporate this into the transparency model.
            # 'P' images are image files with a "palette" colorspace. These
            # should convert nicely to RGB space, for either PNGs or GIFs.
            image = image.convert('RGB')
        if image.mode == 'CMYK':
            # The DeviceCMYK PDF color space has some weird properties. In a
            # future release we can debug these and be smart about it but this
            # is an easy workaround.
            image = image.convert('RGB')

        if image_format in ('PNG', 'GIF'):
            content = Image.make_compressed_image_content(image)
            filter_type = 'FlateDecode'  # TODO use a predictor
        elif image_format == 'JPEG':
            content = Image.make_jpeg_image_content(image)
            filter_type = 'DCTDecode'
        else:
            raise ValueError(
                'Unsupported image format: {}. Supported formats are '
                'PNG, JPEG, and GIF'.format(image.format)
            )

        xobj = PdfDict(
            stream=content,
            BitsPerComponent=8,
            Filter=PdfName(filter_type),
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
    def make_compressed_image_content(image):
        compressed = zlib.compress(Image.get_raw_image_bytes(image))
        return Image.get_decoded_bytes(compressed)

    @staticmethod
    def make_jpeg_image_content(image):
        file_obj = BytesIO()
        # This is the only way to preserve the JPEG encoding. It also seems to
        # recompress the data, so that the raw bytes of this differ from the
        # raw bytes of the original file. It'll probably be better to provide a
        # special wrapper around PILImage that preserves the original bytes so
        # we can just use those for JPEGs. TODO.
        image.save(file_obj, format='JPEG')
        return Image.get_decoded_bytes(file_obj.getvalue())

    @staticmethod
    def get_decoded_bytes(content):
        # Right now, pdfrw needs strings, not bytes like you'd expect in py3,
        # for binary stream objects. This might change in future versions.
        if sys.version_info.major < 3:
            return content
        return content.decode('Latin-1')

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
