# -*- coding: utf-8 -*-
"""
Image annotation type. Though not an official PDF annotation type, images can
easily be added as annotations by drawing Image XObjects in the content stream.
"""
from pdf_annotate.annotations import Annotation


# TODO Image XObject needs to be placed in annotation's /Resources dict
class Image(Annotation):

    @staticmethod
    def transform(location, transform):
        pass

    def get_matrix(self):
        pass

    def get_rect(self):
        pass

    def as_pdf_object(self):
        obj = self.make_base_object()
        # TODO return obj
