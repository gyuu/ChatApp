#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DatabaseError
from celery import Task

from . import (
    socketio,
    celery,
    redis_store,
    config,
)

from .models import Message
from chat.utils import add_offline_msg

engine = create_engine(
    config[os.getenv('FLASK_CONFIG') or 'default'].SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

session = Session()


# @celery.task(name='remove_expired_users')
# def task_remove_expired_users():
#     now = int(time.time())
#     users_removed = redis_store.zremrangebyscore('online_users', 0, now)
#     return users_removed


# @celery.task(name='ping_all_users')
# def task_ping_all_users():
#     socketio.emit('ping', namespace='/chat')


@celery.task
def save_message(message, is_offline=True):
    message['content'] = json.dumps(message['content'])
    msg = Message(**message)
    session.add(msg)
    try:
        session.commit()
        if is_offline:
            add_offline_msg(message['user_id'], msg.id)
        print 'msg %d inserted.' % msg.id
    except DatabaseError as e:
        session.rollback()
        raise e


@celery.task
def load_messages(msg_ids):
    time.sleep(5)
    msgs = [m.to_json() for m in session.query(Message).filter(
        Message.id.in_(msg_ids)
    ).all()]
    return msgs
