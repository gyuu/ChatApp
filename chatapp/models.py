# -*- coding: utf-8 -*-

from . import (
    db,
    config,
)
from sqlalchemy import (
    UniqueConstraint,
    inspect,
)
from sqlalchemy_utils import (
    ChoiceType,
    PhoneNumberType,
    URLType,
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    SignatureExpired
)

# todo: get correct config
DEFAULT_AVATAR = config['default'].DEFAULT_AVATAR
SECRET_KEY = config['default'].SECRET_KEY


class Base(db.Model):
    __abstract__ = True

    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime,
                           default=db.func.now(), onupdate=db.func.now())


class User(Base):
    # attributes
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(128))
    avatar = db.Column(URLType, default=DEFAULT_AVATAR)
    email = db.Column(db.String(50), unique=True)

    groups = db.relationship('Group', backref='user', lazy='dynamic')

    # properties
    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # methods
    def __repr__(self):
        return '<User %r>' % self.username

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=172800):
        """token 有效期 48 小时。"""
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        user_id = User.id_for_token(token)
        if user_id:
            user = User.query.get(user_id)
            return user
        else:
            return None

    @staticmethod
    def id_for_token(token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
            return data['id']
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token

    def get_brief(self):
        return {
            'id': self.id,
            'username': self.username,
            'avatar': self.avatar
        }

    def get_friends(self):
        groups = self.groups.all()
        friends = []
        for g in groups:
            ids = [
                t[0] for t in g.friends.with_entities(FriendShip.friend_id).all()
            ]
            friend_info = [
                u.get_brief() for u in User.query.filter(User.id.in_(ids)).all()
            ]
            friends.append({
                'group_name': g.name,
                'gid': g.id,
                'friends': friend_info,
            })
        return friends

    def add_friend(self, friend_id, group_id=None):
        if not group_id:
            group_id = self.groups.first().id
        friendship = FriendShip(group_id=group_id, friend_id=friend_id)
        db.session.add(friendship)

    def delete_friend(self, friend_id, group_id):
        group = self.groups.filter(Group.id == group_id).first()
        if not group:
            return False
        friend = group.friends.filter(
            FriendShip.friend_id == friend_id).first()
        if not friend:
            return False
        group.friends.remove(friend)
        db.session.delete(friend)
        return True

    def add_group(self, group_name):
        group = Group(user_id=self.id, name=group_name)
        self.groups.append(group)
        db.session.add(group)
        return group

    def delete_group(self, group_id):
        group = self.groups.filter(Group.id == group_id).first()
        if not group:
            return False
        self.groups.remove(group)
        db.session.delete(group)
        return True

    # def is_following(self, user):
    #     return self.following.filter(
    #         following_to_followed.c.followed_user_id == user.id).count() > 0

    # def follow(self, user):
    #     if not self.is_following(user):
    #         self.following.append(user)
    #         return self

    # def unfollow(self, user):
    #     if self.is_following(user):
    #         self.following.remove(user)
    #         return self


class Group(Base):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(20))

    friends = db.relationship('FriendShip', backref='group', lazy='dynamic')

    __table_args__ = (UniqueConstraint('user_id', 'name', name='user_groupname_uc'),
                      )

    def __repr__(self):
        return '<Group %r (user %r): %r>' % (self.id, self.user_id, self.name)


class FriendShip(Base):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    friend_id = db.Column(db.Integer)
    is_set = db.Column(db.Boolean, default=False)

    __table_args__ = (UniqueConstraint('group_id', 'friend_id', name='group_friend_uc'),
                      )

    def __repr__(self):
        return '<FriendShip: group %r, user %r>' % (self.group_id, self.friend_id)


class Message(Base):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    to_user_id = db.Column(db.Integer)
    content = db.Column(db.String(200))

    def __repr__(self):
        return '<Message %r>' % self.id

    def to_json(self):
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'to_user_id': self.to_user_id,
            'content': json.loads(self.content),
        }
