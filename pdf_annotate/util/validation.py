# -*- coding: utf-8 -*-
"""
Provides validation primitives for defining attrs-style "data classes". By
default all the schema types default to (and thus allow) None. Specifying
required attributes isn't yet supported.
"""
import attr
import six


NUMERIC_TYPES = six.integer_types + (float,)


def Boolean(**kwargs):
    _add_validator_to_kwargs(kwargs, instance_of(bool))
    return attr.ib(**kwargs)


def Integer(**kwargs):
    _add_validator_to_kwargs(kwargs, instance_of(six.integer_types))
    return attr.ib(**kwargs)


def Number(**kwargs):
    _add_validator_to_kwargs(kwargs, is_number())
    return attr.ib(**kwargs)


def Enum(values, **kwargs):
    _add_validator_to_kwargs(kwargs, one_of(values))
    return attr.ib(**kwargs)


def String(**kwargs):
    _add_validator_to_kwargs(kwargs, instance_of(str))
    return attr.ib(**kwargs)


def Color(**kwargs):
    """Color value. Can be specified as three-item list/tuple (RGB) or four-
    item list/tuple (RGBA).
    """
    _add_validator_to_kwargs(kwargs, is_color())
    return attr.ib(**kwargs)


def Points(**kwargs):
    _add_validator_to_kwargs(kwargs, is_points_list())
    return attr.ib(**kwargs)


def Field(allowed_type, **kwargs):
    """Generic field, e.g. Field(ContentStream)."""
    _add_validator_to_kwargs(kwargs, instance_of(allowed_type))
    return attr.ib(**kwargs)


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
                if len(point) != 2 or not (
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
        elif not (a <= value <= b):
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


def is_color():
    def validate(obj, attr, value):
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
        elif value is not None:
            raise ValueError('Value ({}) is not a RGB(A) color'.format(value))
    return validate


def _listify(v):
    if isinstance(v, tuple):
        return list(v)
    elif not isinstance(v, list):
        return [v]
    return v


def _tupleize(v):
    if isinstance(v, list):
        return tuple(v)
    elif not isinstance(v, tuple):
        return (v,)
    return v


def _add_validator_to_kwargs(kwargs, validator):
    existing = _listify(kwargs.pop('validator', []))
    existing.append(validator)
    kwargs['validator'] = existing
