# -*- coding: utf-8 -*-
ALLOWED_ALIGNS = ('left', 'center', 'right')
ALLOWED_BASELINES = ('top', 'middle', 'bottom')


class Appearance(object):
    BLACK = (0, 0, 0)
    TRANSPARENT = tuple()

    whitelist_kwargs = frozenset([
        'stroke_color', 'stroke_width', 'border_style', 'fill',
        'dash_array', 'font_size', 'text', 'appearance_stream',
        'image', 'wrap_text', 'text_align', 'text_baseline',
        'line_spacing',
    ])

    def __init__(self, **kwargs):
        self.stroke_color = kwargs.get('stroke_color', self.BLACK)
        self.stroke_width = kwargs.get('stroke_width', 1)
        self.border_style = kwargs.get('border_style', 'S')
        self.fill = kwargs.get('fill', self.TRANSPARENT)
        self.dash_array = kwargs.get('dash_array')
        self.appearance_stream = kwargs.get('appearance_stream')
        self.image = kwargs.get('image')

        self.wrap_text = kwargs.get('wrap_text')
        self.font_size = kwargs.get('font_size')
        self.text = kwargs.get('text')
        self.set_text_align_params(kwargs)
        self.line_spacing = kwargs.get('line_spacing', 1.2)

        for k, v in kwargs.items():
            setattr(self, k, v)

    def copy(self, **kwargs):
        A = Appearance(**kwargs)
        for k, v in self.__dict__.items():
            if k in self.whitelist_kwargs and k not in kwargs:
                setattr(A, k, v)
        return A

    def set_text_align_params(self, kwargs):
        self.text_align = kwargs.get('text_align', 'left')
        # TODO move to a proper configuration framework to stop this madness
        if self.text_align not in ALLOWED_ALIGNS:
            raise ValueError(
                'Invalid text_align property: {}'.format(self.text_align)
            )
        self.text_baseline = kwargs.get('text_baseline', 'middle')
        if self.text_baseline not in ALLOWED_BASELINES:
            raise ValueError(
                'Invalid text_baseline property: {}'.format(self.text_baseline)
            )
