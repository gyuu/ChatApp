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

from .models import (
    Message, Group, User, FriendShip
)
from chat.utils import add_offline_msg

engine = create_engine(
    config[os.getenv('FLASK_CONFIG') or 'default'].SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

session = Session()


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
            add_offline_msg(message['to_user_id'], msg.id)
        print 'msg %d inserted.' % msg.id
    except DatabaseError as e:
        session.rollback()
        raise e


@celery.task
def load_messages(msg_ids):
    time.sleep(5)
    print msg_ids
    msgs = [m.to_json() for m in session.query(Message).filter(
        Message.id.in_(msg_ids)
    ).all()]
    return msgs


@celery.task
def add_friend(payload):
    group_id = payload['group_id']
    friend_id = payload['friend_id']
    group = session.query(Group).filter(Group.id == group_id).first()
    friendship = FriendShip(group_id=group_id, friend_id=friend_id)
    group.friends.append(friendship)
    session.add(friendship)
    session.add(group)
    try:
        session.commit()
        print 'friendship (g %d, u %d) inserted.' % (group_id, friend_id)
    except DatabaseError as e:
        session.rollback()
        raise e
