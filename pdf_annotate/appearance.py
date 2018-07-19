class Appearance(object):
    BLACK = (0, 0, 0)
    TRANSPARENT = tuple()

    def __init__(self, **kwargs):
        self.stroke_color = kwargs.get('stroke_color', self.BLACK)
        self.stroke_width = kwargs.get('stroke_width', 1)
        self.border_style = kwargs.get('border_style', 'S')
        self.fill = kwargs.get('fill', self.TRANSPARENT)
        self.dash_array = kwargs.get('dash_array', None)

        for k, v in kwargs.items():
            setattr(self, k, v)
