# -*- coding: utf-8 -*-
class Appearance(object):
    BLACK = (0, 0, 0)
    TRANSPARENT = tuple()

    whitelist_kwargs = frozenset([
        'stroke_color', 'stroke_width', 'border_style', 'fill',
        'dash_array', 'font_size', 'text', 'appearance_stream',
        'image', 'wrap_text',
    ])

    def __init__(self, **kwargs):
        self.stroke_color = kwargs.get('stroke_color', self.BLACK)
        self.stroke_width = kwargs.get('stroke_width', 1)
        self.border_style = kwargs.get('border_style', 'S')
        self.fill = kwargs.get('fill', self.TRANSPARENT)
        self.dash_array = kwargs.get('dash_array')
        self.font_size = kwargs.get('font_size')
        self.text = kwargs.get('text')
        self.appearance_stream = kwargs.get('appearance_stream')
        self.image = kwargs.get('image')
        self.wrap_text = kwargs.get('wrap_text')

        for k, v in kwargs.items():
            setattr(self, k, v)

    def copy(self):
        A = Appearance()
        for k, v in self.__dict__.items():
            if k in self.whitelist_kwargs:
                setattr(A, k, v)
        return A
