from pdfrw.objects import PdfDict, PdfName
from six import StringIO


ALL_VERSIONS = ('1.3', '1.4', '1.5', '1.6', '1.7')

PRINT_FLAG = 4


class Annotation(object):
    """Base class for all PDF annotation objects.

    There is a lot of nuance and viewer-specific (mostly Acrobat and Bluebeam)
    details to consider when creating PDF annotations. One big thing that's not
    immediately clear from the PDF spec is that wherever possible, we fill in
    the annotations' type-specific details (e.g. BE and IC for squares), but
    also create and include an Appearance Stream. The latter gives us control
    over exactly how the annotation appears across different viewers, while the
    former allows Acrobat or BB to regenerate the appearance stream during
    editing.
    """
    versions = ALL_VERSIONS

    def __init__(self, location, appearance, metadata=None):
        self._location = location
        self._appearance = appearance

    @property
    def page(self):
        return self._location.page

    def validate(self, pdf_version):
        """Validate a new annotation against a given PDF version."""
        pass

    def make_base_object(self):
        """Create the base PDF object with properties that all annotations
        share.
        """
        # TODO add metadata
        return PdfDict(
            **{
                'Type': PdfName('Annot'),
                'Subtype': PdfName(self.subtype),
                'Rect': self.make_rect(),
                # TODO support passing in flags
                'F': PRINT_FLAG,
            }
        )

    def make_ap_dict(self):
        return PdfDict(**{'N': self.make_n_dict()})

    def get_matrix(self):
        raise NotImplementedError()

    def make_n_dict(self):
        return PdfDict(
            stream=self.graphics_commands(),
            **{
                'BBox': self.make_rect(),
                'Resources': PdfDict(**{'ProcSet': PdfName('PDF')}),
                'Matrix': self.get_matrix(),
                'Type': PdfName('XObject'),
                'Subtype': PdfName('Form'),
                'FormType': 1,
            }
        )

    def make_rect(self):
        """Return a bounding box that encompasses the entire annotation."""
        raise NotImplementedError()

    def as_pdf_object(self):
        """Return the PdfDict object representing the annotation."""
        raise NotImplementedError()


def make_border_dict(appearance):
    border = PdfDict(
        **{
            'Type': PdfName('Border'),
            'W': appearance.stroke_width,
            'S': PdfName(appearance.border_style),
        }
    )
    if appearance.dash_array:
        if appearance.border_style != 'D':
            raise ValueError('Dash array only applies to dashed borders!')
        border.D = appearance.dash_array
    return border


class Square(Annotation):
    subtype = 'Square'

    def get_matrix(self):
        stroke_width = self._appearance.stroke_width
        return [
            1, 0, 0, 1,
            -(self._location.x1 - stroke_width),
            -(self._location.y1 - stroke_width),
        ]

    @staticmethod
    def rotate(location, rotate, page_size):
        if rotate == 0:
            return location

        l = location.copy()
        if rotate == 90:
            width = page_size[0]
            l.x1 = width - location.y2
            l.y1 = location.x1
            l.x2 = width - location.y1
            l.y2 = location.x2
        elif rotate == 180:
            width, height = page_size
            l.x1 = width - location.x2
            l.y1 = height - location.y2
            l.x2 = width - location.x1
            l.y2 = height - location.y1
        elif rotate == 270:
            height = page_size[1]
            l.x1 = location.y1
            l.y1 = height - location.x2
            l.x2 = location.y2
            l.y2 = height - location.x1
        return l

    def make_rect(self):
        stroke_width = self._appearance.stroke_width
        return [
            self._location.x1 - stroke_width,
            self._location.y1 - stroke_width,
            self._location.x2 + stroke_width,
            self._location.y2 + stroke_width,
        ]

    def graphics_commands(self):
        stream = StringIO()
        L = self._location
        A = self._appearance
        stream.write('{} {} {} RG '.format(*A.stroke_color))
        stream.write('{} w '.format(A.stroke_width))
        stream.write('{} {} {} {} re S '.format(
            L.x1,
            L.y1,
            L.x2 - L.x1,
            L.y2 - L.y1,
        ))
        # TODO dash array
        # TODO fill
        return stream.getvalue()

    def as_pdf_object(self):
        obj = self.make_base_object()
        A = self._appearance
        obj.BS = make_border_dict(A)
        obj.C = A.stroke_color
        if A.fill:
            obj.IC = A.fill
        obj.AP = self.make_ap_dict()
        padding = A.stroke_width / 2.0
        obj.RD = [padding, padding, padding, padding]
        return obj


class Circle(Annotation):
    subtype = 'Circle'

    @staticmethod
    def rotate(location, rotate, page_size):
        if rotate == 0:
            return location

        l = location.copy()
        if rotate == 90:
            width = page_size[0]
            l.x1 = width - location.y2
            l.y1 = location.x1
            l.x2 = width - location.y1
            l.y2 = location.x2
        elif rotate == 180:
            width, height = page_size
            l.x1 = width - location.x2
            l.y1 = height - location.y2
            l.x2 = width - location.x1
            l.y2 = height - location.y1
        elif rotate == 270:
            height = page_size[1]
            l.x1 = location.y1
            l.y1 = height - location.x2
            l.x2 = location.y2
            l.y2 = height - location.x1
        return l

    def graphics_commands(self):
        L = self._location
        A = self._appearance

        # PDF graphics operators doesn't have an ellipse method, so we have to
        # construct it from four bezier curves
        left_x = L.x1
        right_x = L.x2
        bottom_x = left_x + (right_x - left_x) / 2.0
        top_x = bottom_x

        bottom_y = L.y1
        top_y = L.y2
        left_y = bottom_y + (top_y - bottom_y) / 2.0
        right_y = left_y

        stream = StringIO()
        stream.write('{} {} {} RG '.format(*A.stroke_color))
        stream.write('{} w '.format(A.stroke_width))
        # Move to the bottom of the circle, then four curves around.
        # https://stackoverflow.com/questions/1734745/how-to-create-circle-with-b%C3%A9zier-curves
        cp_offset = 0.552284749831
        stream.write('{} {} m '.format(bottom_x, bottom_y))
        stream.write('{} {} {} {} {} {} c '.format(
            bottom_x + (right_x - bottom_x) * cp_offset, bottom_y,
            right_x, right_y - (right_y - bottom_y) * cp_offset,
            right_x, right_y,
        ))
        stream.write('{} {} {} {} {} {} c '.format(
            right_x, right_y + (top_y - right_y) * cp_offset,
            top_x + (right_x - top_x) * cp_offset, top_y,
            top_x, top_y,
        ))
        stream.write('{} {} {} {} {} {} c '.format(
            top_x - (top_x - left_x) * cp_offset, top_y,
            left_x, left_y + (top_y - left_y) * cp_offset,
            left_x, left_y,
        ))
        stream.write('{} {} {} {} {} {} c '.format(
            left_x, left_y - (left_y - bottom_y) * cp_offset,
            bottom_x - (bottom_x - left_x) * cp_offset, bottom_y,
            bottom_x, bottom_y,
        ))
        stream.write('h S ')
        # TODO dash array
        # TODO fill
        return stream.getvalue()

    def get_matrix(self):
        stroke_width = self._appearance.stroke_width
        return [
            1, 0, 0, 1,
            -(self._location.x1 - stroke_width),
            -(self._location.y1 - stroke_width),
        ]

    def make_rect(self):
        stroke_width = self._appearance.stroke_width
        return [
            self._location.x1 - stroke_width,
            self._location.y1 - stroke_width,
            self._location.x2 + stroke_width,
            self._location.y2 + stroke_width,
        ]

    def as_pdf_object(self):
        obj = self.make_base_object()
        A = self._appearance
        obj.BS = make_border_dict(A)
        obj.C = A.stroke_color
        if A.fill:
            obj.IC = A.fill
        obj.AP = self.make_ap_dict()
        padding = A.stroke_width / 2.0
        obj.RD = [padding, padding, padding, padding]
        return obj


class Line(Annotation):
    subtype = 'Line'

    def make_rect(self):
        stroke_width = self._appearance.stroke_width
        min_x, max_x = sorted([self._location.x1, self._location.x2])
        min_y, max_y = sorted([self._location.y1, self._location.y2])
        return [
            min_x - stroke_width,
            min_y - stroke_width,
            max_x + stroke_width,
            max_y + stroke_width,
        ]

    def get_matrix(self):
        # Note: Acrobat and BB put padding that's not quite the same as the
        # stroke width here. I'm not quite sure why yet, so I'm not changing it.
        stroke_width = self._appearance.stroke_width
        return [
            1, 0, 0, 1,
            -(self._location.x1 - stroke_width),
            -(self._location.y1 - stroke_width),
        ]

    def graphics_commands(self):
        L = self._location
        A = self._appearance

        stream = StringIO()
        stream.write('{} {} {} RG '.format(*A.stroke_color))
        stream.write('{} w '.format(A.stroke_width))
        stream.write('{} {} m '.format(L.x1, L.y1))
        stream.write('{} {} l '.format(L.x2, L.y2))
        stream.write('S')

        return stream.getvalue()

    def as_pdf_object(self):
        obj = self.make_base_object()
        obj.BS = make_border_dict(self._appearance)
        obj.C = self._appearance.stroke_color
        obj.L = [
            self._location.x1, self._location.y1,
            self._location.x2, self._location.y2,
        ]
        obj.AP = self.make_ap_dict()
        # TODO line endings, leader lines, captions
        return obj


def make_points_rect(location, stroke_width):
    p = location.points[0]
    min_x, max_x, min_y, max_y = p[0], p[1], p[0], p[1]
    for x, y in location.points:
        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)
    return [
        min_x - stroke_width,
        min_y - stroke_width,
        max_x + stroke_width,
        max_y + stroke_width,
    ]


class Polygon(Annotation):
    subtype = 'Polygon'
    versions = ('1.5', '1.6', '1.7')

    def make_rect(self):
        return make_points_rect(self._location, self._appearance.stroke_width)

    def get_matrix(self):
        # Note: Acrobat and BB put padding that's not quite the same as the
        # stroke width here. I'm not quite sure why yet, so I'm not changing it.
        rect = self.make_rect()
        return [1, 0, 0, 1, -rect[0], -rect[1]]

    def graphics_commands(self):
        L = self._location
        A = self._appearance
        points = L.points

        stream = StringIO()
        stream.write('{} {} {} RG '.format(*A.stroke_color))
        stream.write('{} w '.format(A.stroke_width))

        stream.write('{} {} m '.format(points[0][0], points[0][1]))
        for x, y in points[1:]:
            stream.write('{} {} l '.format(x, y))
        stream.write('s')

        return stream.getvalue()

    def as_pdf_object(self):
        obj = self.make_base_object()
        obj.BS = make_border_dict(self._appearance)
        obj.C = self._appearance.stroke_color
        if self._appearance.fill:
            obj.IC = self._appearance.fill
        # Flatten list of [[x, y], [x, y], ...]
        obj.Vertices = [v for point in self._location.points for v in point]
        obj.AP = self.make_ap_dict()
        return obj


class Polyline(Annotation):
    subtype = 'PolyLine'
    versions = ('1.5', '1.6', '1.7')

    def make_rect(self):
        return make_points_rect(self._location, self._appearance.stroke_width)

    def as_pdf_object(self):
        # TODO close attribute?
        obj = self.make_base_object()
        obj.BS = make_border_dict(self._appearance)
        obj.C = self._appearance.stroke_color
        if self._appearance.fill:
            obj.IC = self._appearance.fill
        # Flatten list of [[x, y], [x, y], ...]
        obj.Vertices = [v for point in self._location.points for v in point]
        obj.AP = self.make_ap_dict()
        return obj


class Ink(object):
    subtype = 'Ink'


class FreeText(object):
    subtype = 'FreeText'


class Stamp(object):
    subtype = 'Stamp'
