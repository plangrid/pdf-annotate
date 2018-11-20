# -*- coding: utf-8 -*-
from unittest import TestCase

from pdf_annotate import PdfAnnotator
from pdf_annotate.annotations.image import Image
from pdf_annotate.config.appearance import Appearance
from pdf_annotate.config.location import Location
from pdf_annotate.graphics import ContentStream
from pdf_annotate.graphics import CTM
from pdf_annotate.graphics import Restore
from pdf_annotate.graphics import Save
from pdf_annotate.graphics import XObject
from tests.files import PNG_FILES
from tests.files import SIMPLE


class TextExplicitAppearanceStream(TestCase):
    def test_explicit_content_stream(self):
        a = PdfAnnotator(SIMPLE)
        location = Location(x1=50, y1=10, x2=100, y2=200, page=0)
        content_stream = ContentStream([
            Save(),
            CTM(Image.get_ctm(0, location)),
            XObject('MyXObject'),
            Restore(),
        ])
        appearance = Appearance(
            appearance_stream=content_stream,
            xobjects={
                'MyXObject': Image.make_image_xobject(PNG_FILES[0]),
            },
        )

        a.add_annotation(
            'square',
            location=location,
            appearance=appearance,
        )
        a.write('output.pdf')
