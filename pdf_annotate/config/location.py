# -*- coding: utf-8 -*-
import attr

from pdf_annotate.util.validation import Integer
from pdf_annotate.util.validation import Number
from pdf_annotate.util.validation import Points
from pdf_annotate.util.validation import positive


@attr.s
class Location(object):
    page = Integer(required=True, validators=positive)
    points = Points()
    x1 = Number()
    y1 = Number()
    x2 = Number()
    y2 = Number()

    def copy(self):
        L = Location(page=self.page)
        for k, v in self.__dict__.items():
            setattr(L, k, v)
        return L
