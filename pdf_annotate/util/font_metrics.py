# -*- coding: utf-8 -*-
"""
    Font Metrics Utils
    ~~~~~~~~~~

    :copyright: Copyright 2019 Autodesk, Inc.
    :license: MIT, see LICENSE for details.
"""
import attr

from pdf_annotate.util.validation import Number, List, Dict


@attr.s
class FontMetrics:
    """
    Class to hold our font metric calculations.
    """
    italicAngle = Number(default=0)
    usWeightClass = Number(default=500)
    isFixedPitch = Number(default=0)

    unitsPerEm = Number(default=1000)
    scale = Number(default=float(1))
    bbox = List(default=[])

    ascent = Number(default=None)
    descent = Number(default=None)
    capHeight = Number(default=None)

    stemV = Number(default=None)
    defaultWidth = Number(default=None)
    widths = List(default=[])
    cmap = Dict(default={})

    @property
    def flags(self):
        flags = 4
        if self.italicAngle != 0:
            self.flags = self.flags | 64
        if self.usWeightClass >= 600:
            self.flags = self.flags | 262144
        if self.isFixedPitch:
            self.flags = self.flags | 1
        return flags
