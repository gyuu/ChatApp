#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import g, request
from sqlalchemy.exc import DatabaseError
from ..models import User
from .. import db, tokenauth, redis_store
from ..utils import response
from . import auth
from .schemas import (
    RegisterSchema,
    LoginSchema,
)


@tokenauth.verify_token
def verify_token(token):
    g.user = User.verify_auth_token(token)
    if not g.user:
        return False
    return True


@tokenauth.error_handler
def auth_failed():
    errors = {
        'auth': 'missing access_token.'
    }
    return response(401, errors)


@auth.route('/register', methods=['POST'])
def register():
    rs = RegisterSchema()
    user, errors = rs.load(request.get_json(force=True))
    if errors:
        return response(400, errors)
    else:
        token = user.generate_auth_token()
        data = {
            'token': token,
            'uid': user.id
        }
        return response(data=data)


@auth.route('/login', methods=['POST'])
def login():
    ls = LoginSchema()
    user, errors = ls.load(request.get_json(force=True))
    if errors:
        return response(400, errors)
    else:
        token = user.generate_auth_token()
        data = {
            'token': token,
            'uid': user.id,
        }
        return response(data=data)


@auth.route('/test')
@tokenauth.login_required
def test():
    return "Hello, %s!" % g.user.username
