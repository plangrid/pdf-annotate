# -*- coding: utf-8 -*-
"""
Provides validation primitives for defining attrs-style "data classes". By
default all the schema types default to (and thus allow) None. Specifying
required attributes isn't yet supported.
"""
import attr
import six


NUMERIC_TYPES = six.integer_types + (float,)


def Boolean(default=None, allow_none=True, required=False):
    validator = instance_of(bool, allow_none)
    if required:
        return attr.ib(validator=validator)
    return attr.ib(default=default, validator=validator)


def Integer(default=None, validators=tuple(), allow_none=True, required=False):
    validator = (
        _tupleize(validators) +
        (instance_of(six.integer_types, allow_none),)
    )
    if required:
        return attr.ib(validator=validator)
    return attr.ib(default=default, validator=validator)


def Number(default=None, validators=tuple(), required=False):
    validator = _tupleize(validators) + (is_number(),)
    if required:
        return attr.ib(validator=validator)
    return attr.ib(default=default, validator=validator)


def Enum(values, default=None, required=False):
    validator = one_of(values)
    if required:
        return attr.ib(validator=validator)
    return attr.ib(default=default, validator=validator)


def String(default=None, allow_none=True, validators=tuple(), required=False):
    validator = _tupleize(validators) + (instance_of(str, allow_none),)
    if required:
        return attr.ib(validator=validator)
    return attr.ib(default=default, validator=validator)


def Color(default=None, allow_none=True, required=False):
    """Color value. Can be specified as three-item list/tuple (RGB) or four-
    item list/tuple (RGBA).
    """
    validator = is_color(allow_none)
    if required:
        return attr.ib(validator=validator)
    return attr.ib(default=default, validator=validator)


def Points(default=None, allow_none=True, required=False):
    validator = is_points_list(allow_none)
    if required:
        return attr.ib(validator=validator)
    return attr.ib(default=default, validator=validator)


def Field(allowed_type, default=None, required=False):
    """Generic field, e.g. Field(ContentStream)."""
    validator = instance_of(allowed_type)
    if required:
        return attr.ib(validator=validator)
    return attr.ib(default=default, validator=validator)


def is_points_list(allow_none=True):
    def validate(obj, attr, value):
        if value is None:
            if not allow_none:
                raise ValueError('Value ({}) cannot be None')
        elif not isinstance(value, (list, tuple)):
            raise ValueError(
                'Value ({}) must be a list of points'.format(value)
            )
        else:
            for point in value:
                if len(point) != 2 and not (
                    isinstance(point[0], NUMERIC_TYPES) and
                    isinstance(point[1], NUMERIC_TYPES)
                ):
                    raise ValueError(
                        'Value ({}) must be a list of points'.format(value)
                    )
    return validate


def greater_than_eq(i, allow_none=True):
    def validate(obj, attr, value):
        if value is None:
            if not allow_none:
                raise ValueError('Value ({}) cannot be None')
        elif not value >= i:
            raise ValueError('Value ({}) must be >= than {}'.format(value, i))
    return validate


positive = greater_than_eq(0)


def between(a, b, allow_none=True):
    def validate(obj, attr, value):
        if value is None:
            if not allow_none:
                raise ValueError('Value ({}) cannot be None')
        elif not (value >= a and value <= b):
            raise ValueError(
                'Value ({}) must be between {} and {}'.format(value, a, b)
            )
    return validate


def instance_of(types, allow_none=True):
    def validate(obj, attr, value):
        if value is None:
            if not allow_none:
                raise ValueError('Value ({}) cannot be None')
        elif not isinstance(value, _tupleize(types)):
            raise ValueError(
                'Value ({}) must be of type ({})'.format(value, types)
            )
    return validate


def is_number(allow_none=True):
    def validate(obj, attr, value):
        if value is None:
            if not allow_none:
                raise ValueError('Value ({}) cannot be None')
        elif not isinstance(value, NUMERIC_TYPES):
            raise ValueError('Value ({}) must be numeric'.format(value))
    return validate


def one_of(values, allow_none=True):
    def validate(obj, attr, value):
        if value is None:
            if not allow_none:
                raise ValueError('Value ({}) cannot be None')
        elif value not in values:
            raise ValueError(
                'Value ({}) must be in ({})'.format(value, values)
            )
    return validate


def is_color(allow_none=True):
    def validate(obj, attr, value):
        if value is None:
            if not allow_none:
                raise ValueError('Value ({}) cannot be None')
        if isinstance(value, (list, tuple)):
            if len(value) not in (3, 4):
                raise ValueError(
                    'Value ({}) is not a RGB(A) color'.format(value)
                )
            for component in value:
                if not (
                    isinstance(component, NUMERIC_TYPES) and
                    component >= 0 and
                    component <= 1
                ):
                    raise ValueError(
                        'Value ({}) is not a RGB(A) color'.format(value)
                    )
    return validate


def _tupleize(v):
    if isinstance(v, list):
        return tuple(v)
    elif not isinstance(v, tuple):
        return (v,)
    return v
