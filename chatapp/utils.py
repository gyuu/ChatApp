#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import jsonify
from flask_restful import Resource
from . import tokenauth


class ProtectedResource(Resource):

    """
    表示受保护的资源，需要登录才可以查看。
    """
    decorators = [tokenauth.login_required]


def response(error_code=None, errors=None, data=None, **kwargs):
    """
    简化返回信息。
    """
    res = {
        'isSuccess': True,
        'data': data,
    }
    if error_code:
        res.update({
            'isSuccess': False,
            'error_code': error_code,
            'error_message': errors,
        })
    return jsonify(**res)


def error_not_found(field_name):
    return response(400, errors={field_name: 'not found.'})


def error_insertion_failed():
    return response(500, errors=dict(database='insertion failed.'))
