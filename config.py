import os
from datetime import timedelta

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tagbook secret'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DEFAULT_AVATAR = 'static/img/fuck.jpg'
    REDIS_URL = 'redis://localhost:6379/0'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://chat:123456@localhost/chat'


config = {
    'development': DevelopmentConfig,

    'default': DevelopmentConfig
}
