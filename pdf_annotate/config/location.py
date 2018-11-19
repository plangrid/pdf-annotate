# -*- coding: utf-8 -*-
# TODO this is super unclear how these are used


class Location(object):

    whitelist_kwargs = frozenset(['points', 'x1', 'y1', 'x2', 'y2', 'page'])

    def __init__(self, **kwargs):
        if 'page' not in kwargs:
            raise ValueError('Must set page on annotations')

        if 'rotation' in kwargs:
            raise ValueError('"rotation" is a reserved attribute')

        for k, v in kwargs.items():
            if k not in self.whitelist_kwargs:
                raise ValueError('Invalid Location kwarg: {}'.format(k))
            setattr(self, k, v)

        self.rotation = 0

    def copy(self):
        L = Location(page=self.page)
        for k, v in self.__dict__.items():
            if k in self.whitelist_kwargs:
                setattr(L, k, v)
        return L
