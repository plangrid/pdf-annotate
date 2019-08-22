# -*- coding: utf-8 -*-
"""
    Font Metrics Utils
    ~~~~~~~~~~

    :copyright: Copyright 2019 Autodesk, Inc.
    :license: MIT, see LICENSE for details.
"""
from fontTools.ttLib import TTFont


class FontMetrics:
    def __init__(self, path):
        self.ttfPath = path
        self.ttfFont = TTFont(self.ttfPath)

        self.italicAngle = None
        self.usWeightClass = None
        self.isFixedPitch = None

        self.unitsPerEm = None
        self.scale = None
        self.bbox = []

        self.ascent = None
        self.descent = None
        self.capHeight = None

        self.stemV = None
        self.defaultWidth = None

        self._calculate()

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

    def _calculate(self):
        # Font Header Table
        self.unitsPerEm = self.ttfFont['head'].unitsPerEm
        self.scale = 1000 / float(self.unitsPerEm)
        x_min = self.ttfFont['head'].xMin
        y_min = self.ttfFont['head'].yMin
        x_max = self.ttfFont['head'].xMax
        y_max = self.ttfFont['head'].yMax
        self.bbox = [
            (x_min * self.scale),
            (y_min * self.scale),
            (x_max * self.scale),
            (y_max * self.scale)
        ]

        # hhead metrics table, these seem to be used instead of OS/2 for compatibility reasons
        if 'hhea' in self.ttfFont:
            self.ascent = self.ttfFont['hhea'].ascent * self.scale
            self.descent = self.ttfFont['hhea'].descent * self.scale

        # OS/2 and Windows metrics table
        if 'OS/2' in self.ttfFont:
            self.usWeightClass = self.ttfFont['OS/2'].usWeightClass
            if not self.ascent:
                self.ascent = self.ttfFont['OS/2'].sTypoAscender * self.scale
            if not self.descent:
                self.descent = self.ttfFont['OS/2'].sTypoDescender * self.scale
            if self.ttfFont['OS/2'].version > 1:
                self.capHeight = self.ttfFont['OS/2'].sCapHeight * self.scale
            else:
                self.capHeight = self.ascent
        else:
            self.usWeightClass = 500
            if not self.ascent:
                self.ascent = y_max * self.scale
            if not self.descent:
                self.descent = y_min * self.scale
            self.capHeight = self.ascent
        self.stemV = 50 + int(pow((self.usWeightClass / 65.0), 2))

        # Post table
        self.isFixedPitch = self.ttfFont['post'].isFixedPitch
        self.italicAngle = self.ttfFont['post'].italicAngle

        # hmtx - contains advance width and left side bearing for each glyph
        self.defaultWidth = self.ttfFont['hmtx'].metrics['.notdef'][0]

        # Character map
        cmap = self.ttfFont['cmap'].getBestCmap()
        self.cmap = cmap

        # Widths
        glyph_set = self.ttfFont.getGlyphSet()
        cids = [cid for cid in cmap]
        if len(cids) <= 0:
            raise MetricsParsingError("Couldn't find any characters in font")
        self.widths = self._format_widths(glyph_set, cmap, cids)

    @staticmethod
    def _format_widths(glyph_set, cmap, cids):
        """
        See Section 9.7.4.3 Glyph Metrics in CIDFonts
        This function will take a uniform list of widths and format it to the PDF compacted format.
        The widths use one of two formats for each segment.
        For varying widths: c [w1 w2 .. wn]
        For constant widths: cfirst clast w
        ie. [ 120 [ 400 325 500 ] 7080 8032 1000 ]
        Would have 120 be 400, 121 be 325, 122 be 500 and 7080 to 8032 all be 1000 width
        :return: A list of lists conforming to the PDF compacted format for widths.
        """
        cids_length = len(cids)
        if cids_length == 0:
            return []
        cids.sort()
        start = 0
        i = 1
        # See Section 9.7.4.3 Glyph Metrics in CIDFonts
        # The widths use one of two formats for each segment.
        # For varying widths: c [w1 w2 .. wn]
        # For constant widths: cfirst clast w
        # ie. [ 120 [ 400 325 500 ] 7080 8032 1000 ]
        # Would have 120 be 400, 121 be 325, 122 be 500 and 7080 to 8032 all be 1000 width
        widths = []
        while True:
            if i >= cids_length or (cids[i] - cids[i - 1] > 1):
                indices = [x for x in range(cids[start], cids[i - 1] + 1)]
                w = [glyph_set[cmap[index]].width for index in indices]

                if len(set(w)) == 1:
                    # Append a 'cfirst clast w' style width to our width segments
                    widths.append(cids[start])
                    widths.append(cids[i - 1])
                    widths.append(w[0])
                else:
                    # Append a 'c [w1 w2 .. wn]' style width to our width segments
                    widths.append(cids[start])
                    widths.append(w)

                # No more ranges
                if i >= cids_length:
                    break

                start = i
            i = i + 1
        return widths


class MetricsParsingError(Exception):
    pass
