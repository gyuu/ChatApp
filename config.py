import os
from datetime import timedelta

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tagbook secret'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DEFAULT_AVATAR = u'http://imgsrc.baidu.com/forum/w=580/sign=dcfad09a209759ee4a5060c382fa434e/b84eb9a1cd11728b931038b5cefcc3cec3fd2c32.jpg'
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
