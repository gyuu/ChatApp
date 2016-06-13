#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.exc import DatabaseError
from marshmallow import fields
from marshmallow.exceptions import ValidationError
from marshmallow.decorators import (
    validates,
    validates_schema,
    post_load,
)
from flask import g

from .. import db
from ..models import User
from ..schemas import BaseSchema

from .validators import (
    wrapper,
    validate_existence,
)


class RegisterSchema(BaseSchema):

    """
    注册。
    """
    username = fields.Str(required=True,
                          validate=wrapper(
                              validate_existence,
                              field_name='username',
                              should_exist=False
                          ))
    password = fields.Str(load_only=True, required=True)
    email = fields.Email(required=True,
                         validate=wrapper(
                             validate_existence,
                             field_name='email',
                             should_exist=False
                         ))
    avatar = fields.URL()

    def load(self, *args, **kwargs):
        """
        使用 try-except 的理由：
        在其他情况正常时，捕获奇奇怪怪的数据库插入错误。
        """
        try:
            return super(RegisterSchema, self).load(*args, **kwargs)
        except ValidationError as err:
            errors = {'database': err.message}
            return (None, errors)

    # json to model
    @post_load
    def create_user(self, data):
        """
        对 load 方法的返回值进行处理，使其返回一个 User 对象。
        如果无法插入，则返回一个 (None, errors)
        """
        user = User(**data)
        db.session.add(user)
        try:
            db.session.commit()
            return user
        except DatabaseError as e:
            print e
            db.session.rollback()
            raise ValidationError('insertion failed.')


class LoginSchema(BaseSchema):

    """
    登录。
    """
    username = fields.Str(required=True,
                          validate=wrapper(
                              validate_existence,
                              field_name='username',
                              should_exist=True
                          ))
    password = fields.Str(required=True)

    def load(self, *args, **kwargs):
        """
        重载 load 方法，使得通过验证之后直接返回 user 对象。
        """
        data, errors = super(LoginSchema, self).load(*args, **kwargs)
        if not errors:
            user = User.query.filter(
                User.username == data['username']).first()
            if user.verify_password(data['password']):
                return (user, errors)
            else:
                errors = {'password': 'wrong password.'}
                return (None, errors)
        else:
            return (None, errors)
