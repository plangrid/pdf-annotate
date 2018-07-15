from pdfrw.objects import PdfDict, PdfName


ALL_VERSIONS = ('1.3', '1.4', '1.5', '1.6', '1.7')


class Annotation(object):

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

    def make_rect(self):
        return [
            self._location.x,
            self._location.y,
            self._location.x + self._appearance.width,
            self._location.y + self._appearance.height,
        ]

    def as_pdf_object(self):
        obj = self.make_base_object()
        obj.BS = make_border_dict(self._appearance)
        obj.C = self._appearance.stroke_color
        if self._appearance.fill:
            obj.IC = self._appearance.fill
        return obj


class Circle(Annotation):
    subtype = 'Circle'

    def make_rect(self):
        return [
            self._location.x,
            self._location.y,
            self._location.x + self._appearance.width,
            self._location.y + self._appearance.height,
        ]

    def as_pdf_object(self):
        obj = self.make_base_object()
        obj.BS = make_border_dict(self._appearance)
        obj.C = self._appearance.stroke_color
        if self._appearance.fill:
            obj.IC = self._appearance.fill
        return obj


class Line(Annotation):
    subtype = 'Line'

    def make_rect(self):
        min_x, max_x = sorted([self._location.x1, self._location.x2])
        min_y, max_y = sorted([self._location.y1, self._location.y2])
        return [min_x, min_y, max_x, max_y]

    def as_pdf_object(self):
        obj = self.make_base_object()
        obj.BS = make_border_dict(self._appearance)
        obj.C = self._appearance.stroke_color
        obj.L = [
            self._location.x1, self._location.y1,
            self._location.x2, self._location.y2,
        ]
        # TODO line endings, leader lines, captions
        return obj


def make_points_rect(location):
    min_x, max_x, min_y, max_y = 0, 0, 0, 0
    for x, y in location.points:
        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)
    return [min_x, min_y, max_x, max_y]


class Polygon(Annotation):
    subtype = 'Polygon'
    versions = ('1.5', '1.6', '1.7')

    def make_rect(self):
        return make_points_rect(self._location)

    def as_pdf_object(self):
        obj = self.make_base_object()
        obj.BS = make_border_dict(self._appearance)
        obj.C = self._appearance.stroke_color
        if self._appearance.fill:
            obj.IC = self._appearance.fill
        # Flatten list of [[x, y], [x, y], ...]
        obj.Vertices = [v for point in self._location.points for v in point]
        return obj


class Polyline(Annotation):
    subtype = 'PolyLine'
    versions = ('1.5', '1.6', '1.7')

    def make_rect(self):
        return make_points_rect(self._location)

    def as_pdf_object(self):
        # TODO close attribute?
        obj = self.make_base_object()
        obj.BS = make_border_dict(self._appearance)
        obj.C = self._appearance.stroke_color
        if self._appearance.fill:
            obj.IC = self._appearance.fill
        # Flatten list of [[x, y], [x, y], ...]
        obj.Vertices = [v for point in self._location.points for v in point]
        return obj


class Ink(object):
    subtype = 'Ink'


class FreeText(object):
    subtype = 'FreeText'


class Stamp(object):
    pass
