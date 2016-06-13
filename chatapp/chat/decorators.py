#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
from flask import request
from flask_socketio import disconnect

from ..models import User
from .utils import save_last_active_time


def authenticated_only(f):
    """
    client 每次发送的 json 中都要加上 token 来标识身份。
    为了使用这个 decorator，每个 handler 都需要一个 payload 参数。
    """
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        # args 是参数 tuple，如果只有一个参数那么参数为 args[0]。
        payload = args[0]
        token = payload.pop('token', None)
        if not token:
            disconnect()
        else:
            user_id = User.id_for_token(token)
            if not user_id:
                disconnect()
            else:
                payload['user_id'] = user_id
                return f(*args, **kwargs)
    return wrapped


def track_activity(f):
    """
    记录用户的最后一次活动时间，用于重新登录之后获取离线消息。
    """
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        user_id = args[0]['user_id']
        save_last_active_time(user_id)
        return f(*args, **kwargs)
    return wrapped
