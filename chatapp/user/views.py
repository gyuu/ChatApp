# -*- coding: utf-8 -*-

import os
from flask import g, request
from sqlalchemy.exc import DatabaseError
from werkzeug import secure_filename
from ..models import User, Group
from .. import db, tokenauth, socketio

from ..utils import (
    response, error_insertion_failed,
    error_not_found,
)

from ..redis_utils import (
    is_user_online,
)

from .utils import (
    UPLOAD_FOLDER,
    allowed_file,
)
from . import userbp


@userbp.route('/profile')
@tokenauth.login_required
def profile():
    user = g.user
    return response(data=user.get_brief())


@userbp.route('/find', methods=['POST'])
@tokenauth.login_required
def find_user():
    username = request.json.get('username')
    if not username:
        return response(400, {'username': 'missing username.'})
    user = User.query.filter(User.username == username).first()
    if not user or user == g.user:
        return error_not_found('user')
    return response(data=user.get_brief())


@userbp.route('/findbyid', methods=['POST'])
@tokenauth.login_required
def find_user_by_id():
    user_id = request.json.get('user_id')
    print user_id
    if not user_id:
        return response(400, {'user_id': 'missing user_id.'})
    user = User.query.get(user_id)
    if not user:
        return error_not_found('user')
    return response(data=user.get_brief())


@userbp.route('/friends')
@tokenauth.login_required
def friends():
    user = g.user
    return response(data=user.get_friends())


@userbp.route('/add-friend', methods=['POST'])
@tokenauth.login_required
def add_friend():
    friend_id = request.json.get('friend_id')
    group_id = request.json.get('group_id')
    g.user.add_friend(friend_id, group_id)
    try:
        db.session.commit()
        sid, is_online = is_user_online(friend_id)
        print sid, is_online
        if is_online:
            socketio.emit(
                'add-friend-request', {'user_id': g.user.id}, room=sid, namespace='/chat')
        return response(data={'info': 'operation succeeded.'})
    except DatabaseError as e:
        print e
        db.session.rollback()
        return error_insertion_failed()


@userbp.route('/delete-friend', methods=['POST'])
@tokenauth.login_required
def delete_friend():
    group_id = request.json.get('group_id', -1)
    friend_id = request.json.get('friend_id', -1)
    if group_id and friend_id and g.user.delete_friend(friend_id, group_id):
        try:
            db.session.commit()
            return response(data={'info': 'operation succeeded.'})
        except DatabaseError:
            print e
            db.session.rollback()
            return error_insertion_failed()
    else:
        errors = {
            'info': 'bad request.',
        }
        return response(400, errors)


@userbp.route('/add-group', methods=['POST'])
@tokenauth.login_required
def add_group():
    group_name = request.json.get('group_name')
    group = g.user.add_group(group_name)
    try:
        db.session.commit()
        data = {
            'gid': group.id
        }
        return response(data=data)
    except DatabaseError as e:
        print e
        db.session.rollback()
        return error_insertion_failed()


@userbp.route('/delete-group', methods=['POST'])
@tokenauth.login_required
def delete_group():
    group_id = request.json.get('group_id', -1)
    if group_id and g.user.delete_group(group_id):
        try:
            db.session.commit()
            return response(data={'info': 'operation succeeded.'})
        except DatabaseError:
            print e
            db.session.rollback()
            return error_insertion_failed()
    else:
        return error_not_found('group')


@userbp.route('/avatar', methods=['POST'])
@tokenauth.login_required
def upload():
    f = request.files['file']
    if f and allowed_file(f.filename):
        filename = secure_filename(f.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        f.save(filepath)
        file_url = '/'.join(filepath.rsplit('/', 3)[-3:])
        g.user.avatar = file_url
        try:
            db.session.add(g.user)
            db.session.commit()
            return response(data={'file': filename})
        except DatabaseError as e:
            print e
            db.session.rollback()
            return error_insertion_failed()
    else:
        return response(400, {'file': 'invalid file'})
