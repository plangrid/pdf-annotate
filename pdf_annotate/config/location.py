# -*- coding: utf-8 -*-
import attr

from pdf_annotate.util.validation import Integer
from pdf_annotate.util.validation import Number
from pdf_annotate.util.validation import Points
from pdf_annotate.util.validation import positive


@attr.s
class Location(object):
    page = Integer(validator=positive)
    points = Points(default=None)
    x1 = Number(default=None)
    y1 = Number(default=None)
    x2 = Number(default=None)
    y2 = Number(default=None)

    def copy(self):
        L = Location(page=self.page)
        for k, v in self.__dict__.items():
            setattr(L, k, v)
        return L
