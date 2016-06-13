#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import msm


class BaseSchema(msm.Schema):

    """
    将 errors 中的列表转换成单个值，让返回的 json 易于解析。
    """

    def load(self, *args, **kwargs):
        data, errors = super(BaseSchema, self).load(*args, **kwargs)
        if errors:
            for key in errors:
                errors[key] = errors[key][0]
            return (None, errors)
        else:
            return (data, errors)

    def validate(self, *args, **kwargs):
        errors = super(BaseSchema, self).validate(*args, **kwargs)
        if errors:
            for key in errors:
                errors[key] = errors[key][0]
        return errors
