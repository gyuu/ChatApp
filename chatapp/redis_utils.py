#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from . import redis_store

ONLINE_USERS_KEY = 'online_users'
SID_UID_HASH_KEY = 'sid_uid'
USER_LOGOUT_TIME_KEY = 'last_active'
USER_OFFLINE_MSG_KEY = 'user_%d_msg'


def mark_online(sid, user_id):
    old_sid = redis_store.hget(SID_UID_HASH_KEY, user_id)
    if not old_sid:
        r = redis_store.pipeline()
        r.hset(SID_UID_HASH_KEY, user_id, sid)
        r.sadd(ONLINE_USERS_KEY, sid)
        r.execute()
    else:
        r = redis_store.pipeline()
        r.srem(ONLINE_USERS_KEY, old_sid)
        r.hset(SID_UID_HASH_KEY, user_id, sid)
        r.sadd(ONLINE_USERS_KEY, sid)
        r.execute()


def save_last_active_time(user_id):
    now = int(time.time())
    redis_store.hset(USER_LOGOUT_TIME_KEY, user_id, now)


def delete_connection(sid):
    r = redis_store.pipeline()
    r.srem(ONLINE_USERS_KEY, sid)
    r.hdel(SID_UID_HASH_KEY, sid)
    r.execute()


def get_sid(user_id):
    return redis_store.hget(SID_UID_HASH_KEY, user_id)


def is_user_online(user_id):
    sid = get_sid(user_id)
    if sid:
        return sid, redis_store.sismember(ONLINE_USERS_KEY, sid)
    return None, False


def add_offline_msg(user_id, message_id):
    user_msg_key = USER_OFFLINE_MSG_KEY % user_id
    redis_store.sadd(user_msg_key, message_id)


def get_offline_msg(user_id):
    user_msg_key = USER_OFFLINE_MSG_KEY % user_id
    return [int(s) for s in redis_store.smembers(user_msg_key)]


def remove_offline_msg(user_id):
    """
    离线消息被读了之后，取消掉这个 key。
    """
    user_msg_key = USER_OFFLINE_MSG_KEY % user_id
    redis_store.delete(user_msg_key)
