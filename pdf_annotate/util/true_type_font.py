# -*- coding: utf-8 -*-
"""
    True Type Fonts Utility Class
    ~~~~~~~~~~

    :copyright: Copyright 2019 Autodesk, Inc.
    :license: MIT, see LICENSE for details.
"""
import copy

from fontTools.subset import Subsetter
from fontTools.ttLib import TTFont

from pdf_annotate.util.font_metrics import FontMetrics

# Subsetted fonts have 6 random letters prepended to their names
# See section 9.6.4 - Font Subsets of the PDF 1.7 Spec
_FONT_NAME_PREFIX = 'RXMLFT+'
_FONT_CACHE = {}


def get_true_type_font(path, font_name):
    """Helper to avoid having to reload font from disk multiple times in a session

    :param str path: path to .ttf font file
    :param str font_name: name of the font to be included in the PDF file
    :returns TrueTypeFont:
    """
    key = (path, font_name)
    font = _FONT_CACHE.get(key)
    if font is not None:
        return font

    font = TrueTypeFont(path, font_name)
    _FONT_CACHE[key] = font
    return font


def get_subset_true_type_font(text, path, font_name):
    """Helper to avoid having to reload font from disk multiple times in a session

    :param str text: the glyphs to include in the subsetted font
    :param str path: path to .ttf font file
    :param str font_name: name of the font to be included in the PDF file
    :returns SubsetTrueTypeFont:
    """
    subset_font_name = _FONT_NAME_PREFIX + font_name
    key = (path, subset_font_name)
    font = _FONT_CACHE.get(key)
    if font is not None:
        # Ensure this font was created with the appropriate glyphs
        if set(text).issubset(set(font.text)):
            return font
        # TODO: subclass
        raise Exception('A suitable subset font was not found with these glyphs')

    # TODO: subclass
    raise Exception('A suitable subset font was not found with these glyphs')


def create_and_cache_subset_font(text, path, font_name):
    """
    Helper to create a subsetted true type font including the glyphs for the passed in text.
    :param str text: The glyphs to be included in the subset font.
    :param str path: path to .ttf font file
    :param str font_name: name of the font to be included in the PDF file
    :return: SubsetTrueTypeFont:
    """
    subset_font_name = _FONT_NAME_PREFIX + font_name
    key = (path, subset_font_name)

    full_font = get_true_type_font(path, font_name)
    font = SubsetTrueTypeFont(text, full_font)
    _FONT_CACHE[key] = font
    return font


class MetricsParsingError(Exception):
    pass


class TrueTypeFont:
    """
    Used to load a true type font and calculate font metrics from it that are
    needed to embed the font program in a PDF.
    """

    def __init__(self, path, font_name):
        self.font_name = font_name
        self.ttf_font = TTFont(path)

        self._metrics = None
        self._font_glyph_set = None

    @property
    def _glyph_set(self):
        if self._font_glyph_set is None:
            self._font_glyph_set = self.ttf_font.getGlyphSet()

        return self._font_glyph_set

    @property
    def metrics(self):
        # Lazy load metrics as it can take a long time to calculate on a large font if we only need it for the subset
        if self._metrics is None:
            self._metrics = self._calculate(self.ttf_font)

        return self._metrics

    def get_glyph_id(self, glyph_name):
        """
        Wrapper for getting a glyph name via font tools.
        :param glyph_name: The name of the glyph we're retrieving.
        :return: The corresponding glyph ID.
        """
        return self.ttf_font['glyf'].getGlyphID(glyph_name)

    def measure_text(self, text, font_size):
        """Measure a block of text using the font's metrics. If the text
        contains characters the font does not define, the .notdef character's
        width is used.

        :param str text: The text to measure
        :param int|None font_size: Font size (in em units) to scale
            measurements.
        :returns int: width of text
        """
        if font_size is None:
            raise ValueError('Font size must be specified')

        total_width = 0
        notdef_width = self._glyph_set['.notdef'].width
        for character in text:
            # If the cmap doesn't contain the character, this'll just return
            # None for the glyph and use .notdef
            glyph = self._glyph_set.get(self.metrics.cmap.get(ord(character)))
            total_width += glyph.width if glyph is not None else notdef_width
        # Scale total width by font size
        return total_width * font_size / self.metrics.unitsPerEm

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


class SubsetTrueTypeFont(TrueTypeFont):
    """
    Used to load a true type font and calculate font metrics from it that are
    needed to embed the font program in a PDF.
    """

    def __init__(self, text, font):
        self.font_name = _FONT_NAME_PREFIX + font.font_name

        # Create a subset of the true type font based on the characters we need
        ttf_font = copy.deepcopy(font.ttf_font)
        subsetter = Subsetter()
        subsetter.populate(text=text)
        subsetter.subset(ttf_font)
        self.ttf_font = ttf_font

        self._metrics = None
        self._font_glyph_set = None
        self.text = text
