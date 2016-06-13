#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import (
    db,
    msm,
)
from ..models import User
from sqlalchemy.sql import exists
from marshmallow.decorators import validates
from marshmallow import fields
from marshmallow.exceptions import ValidationError
from phonenumbers import parse as parse_phonenumber
from sqlalchemy_utils import PhoneNumber
from functools import partial


def validate_existence(value, field_name, should_exist):

    try:
        field = getattr(User, field_name)
    except AttributeError:
        raise ValidationError('no such field.' % field_name)

    exist = db.session.query(exists().where(field == value)).scalar()
    if should_exist and not exist:
        raise ValidationError('%s does not exist.' % field_name)
    elif not should_exist and exist:
        raise ValidationError('%s exists.' % field_name)


def wrapper(func, field_name, should_exist):
    def f(*args, **kwargs):
        func(*args, should_exist=should_exist, field_name=field_name, **kwargs)
    return f
