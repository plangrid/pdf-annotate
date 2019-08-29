# -*- coding: utf-8 -*-
"""
    True Type Fonts Utility Class
    ~~~~~~~~~~

    :copyright: Copyright 2019 Autodesk, Inc.
    :license: MIT, see LICENSE for details.
"""
from fontTools.ttLib import TTFont
from pdf_annotate.util.font_metrics import FontMetrics


class TrueTypeFont:
    """
    Used to load a true type font and calculate font metrics from it that are
    needed to embed the font program in a PDF.
    """
    def __init__(self, path, font_name):
        self.ttfPath = path
        self._ttfFont = TTFont(self.ttfPath)
        # Subsetted fonts have 6 random letters prepended to their names
        # See section 9.6.4 - Font Subsets of the PDF 1.7 Spec
        self.fontName = 'RXMLFT+' + font_name

        self.metrics = self._calculate(self._ttfFont)

    def get_glyph_id(self, glyph_name):
        """
        Wrapper for getting a glyph name via font tools.
        :param glyph_name: The name of the glyph we're retrieving.
        :return: The corresponding glyph ID.
        """
        return self._ttfFont['glyf'].getGlyphID(glyph_name)

    @staticmethod
    def _calculate(font):
        """
        Calculates metrics about our true type font.  These calculations are taken from
        previous work done in the mpdf/fpdf projects.
        :param font: The fonttools font object.
        :return: A FontMetrics object containing the calculated metrics.
        """
        # Font Header Table
        units_per_em = font['head'].unitsPerEm
        scale = 1000 / float(units_per_em)
        x_min = font['head'].xMin
        y_min = font['head'].yMin
        x_max = font['head'].xMax
        y_max = font['head'].yMax
        bbox = [
            (x_min * scale),
            (y_min * scale),
            (x_max * scale),
            (y_max * scale)
        ]

        # hhead metrics table, these seem to be used instead of OS/2 for compatibility reasons
        if 'hhea' in font:
            ascent = font['hhea'].ascent * scale
            descent = font['hhea'].descent * scale

        # OS/2 and Windows metrics table
        if 'OS/2' in font:
            us_weight_class = font['OS/2'].usWeightClass
            if not ascent:
                ascent = font['OS/2'].sTypoAscender * scale
            if not descent:
                descent = font['OS/2'].sTypoDescender * scale
            if font['OS/2'].version > 1:
                cap_height = font['OS/2'].sCapHeight * scale
            else:
                cap_height = ascent
        else:
            us_weight_class = 500
            if not ascent:
                ascent = y_max * scale
            if not descent:
                descent = y_min * scale
            cap_height = ascent
        stem_v = 50 + int(pow((us_weight_class / 65.0), 2))

        # Post table
        is_fixed_pitch = font['post'].isFixedPitch
        italic_angle = font['post'].italicAngle

        # hmtx - contains advance width and left side bearing for each glyph
        default_width = font['hmtx'].metrics['.notdef'][0]

        # Character map
        cmap = font['cmap'].getBestCmap()

        # Widths
        glyph_set = font.getGlyphSet()
        cids = [cid for cid in cmap]
        if len(cids) <= 0:
            raise MetricsParsingError("Couldn't find any characters in font")
        widths = TrueTypeFont._format_widths(glyph_set, cmap, cids)

        return FontMetrics(
            italicAngle=italic_angle,
            usWeightClass=us_weight_class,
            isFixedPitch=is_fixed_pitch,
            unitsPerEm=units_per_em,
            scale=scale,
            bbox=bbox,
            ascent=ascent,
            descent=descent,
            capHeight=cap_height,
            stemV=stem_v,
            defaultWidth=default_width,
            widths=widths,
            cmap=cmap,
        )

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
