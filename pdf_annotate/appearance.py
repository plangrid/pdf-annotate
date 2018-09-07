# -*- coding: utf-8 -*-
class Appearance(object):
    BLACK = (0, 0, 0)
    TRANSPARENT = tuple()

    whitelist_kwargs = frozenset([
        'stroke_color', 'stroke_width', 'border_style', 'fill',
        'dash_array', 'font_size', 'text', 'appearance_stream',
        'image',
    ])

    def __init__(self, **kwargs):
        self.stroke_color = kwargs.get('stroke_color', self.BLACK)
        self.stroke_width = kwargs.get('stroke_width', 1)
        self.border_style = kwargs.get('border_style', 'S')
        self.fill = kwargs.get('fill', self.TRANSPARENT)
        self.dash_array = kwargs.get('dash_array', None)
        self.font_size = kwargs.get('font_size', None)
        self.text = kwargs.get('text', None)
        self.appearance_stream = kwargs.get('appearance_stream', None)
        self.image = kwargs.get('image', None)

        for k, v in kwargs.items():
            setattr(self, k, v)

    def copy(self):
        A = Appearance()
        for k, v in self.__dict__.items():
            if k in self.whitelist_kwargs:
                setattr(A, k, v)
        return A
