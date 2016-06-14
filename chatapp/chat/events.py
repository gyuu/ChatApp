#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import request, render_template
from flask_socketio import (
    send, emit, disconnect,
    rooms, join_room, leave_room, close_room,
)
from .. import socketio, redis_store
from ..models import User
from ..tasks import (
    save_message,
    load_messages,
)
from .decorators import (
    authenticated_only,
    track_activity,
)
from .utils import (
    mark_online,
    delete_connection,
    get_sid,
    is_user_online,
    get_offline_msg,
    remove_offline_msg,
)
from . import chat


@socketio.on('connect', namespace='/chat')
def connect_handler():
    emit('conn_ack', 'OK')


@socketio.on('disconnect', namespace='/chat')
def disconnect_handler():
    delete_connection(request.sid)


@socketio.on('login', namespace='/chat')
@authenticated_only
@track_activity
def login_handler(payload):
    mark_online(request.sid, payload['user_id'])
    offline_msg_ids = get_offline_msg(payload['user_id'])
    if offline_msg_ids:
        load_messages.apply_async((offline_msg_ids,), task_id=request.sid)
        emit('login_ack', {'offline-msg': True})
    else:
        emit('login_ack', {'offline-msg': False})


@socketio.on('offline-msg', namespace='/chat')
@authenticated_only
@track_activity
def offline_msg_handler(payload):
    result = load_messages.AsyncResult(request.sid)
    res = {
        'status': result.state,
    }
    if result.state == 'SUCCESS':
        res['data'] = result.info
        emit('offline-msg-ack', res)
    else:
        emit('offline-msg-ack', res)


@socketio.on('offline-msg-read', namespace='/chat')
@authenticated_only
@track_activity
def offline_msg_read_handler(payload):
    remove_offline_msg(payload['user_id'])


@socketio.on('send', namespace='/chat')
@authenticated_only
@track_activity
def sendmsg_handler(payload):
    """
    没有创建 room，直接对用户所属的 room 发送消息了。
    """
    to_user_id = payload['to_user_id']
    sid, is_online = is_user_online(to_user_id)
    if not is_online:
        save_message.delay(payload)
    else:
        save_message.delay(payload, is_offline=False)
        send(payload, room=sid)
