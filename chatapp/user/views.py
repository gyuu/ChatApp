# -*- coding: utf-8 -*-

from flask import g, request
from sqlalchemy.exc import DatabaseError
from ..models import User, Group
from .. import db, tokenauth
from ..utils import (
    response, error_insertion_failed,
    error_not_found,
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
