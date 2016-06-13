from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
# from flask_restful import Api as API
from flask.ext.httpauth import HTTPTokenAuth
from flask.ext.redis import FlaskRedis
from flask_socketio import SocketIO
from celery import Celery
from config import config, Config


db = SQLAlchemy()
msm = Marshmallow()
tokenauth = HTTPTokenAuth('Token')
socketio = SocketIO()
redis_store = FlaskRedis()
celery = Celery(
    __name__, broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND)


def create_app(config_name):
    app = Flask(__name__)
    config_option = config[config_name]
    app.config.from_object(config_option)
    config_option.init_app(app)

    # extension initializations.
    db.init_app(app)
    msm.init_app(app)
    socketio.init_app(app)
    redis_store.init_app(app)
    celery.conf.update(app.config)

    from .auth import auth as auth_blueprint
    from .user import userbp as user_blueprint
    from .index import indexbp as index_blueprint
    app.register_blueprint(index_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(user_blueprint, url_prefix='/user')

    return app
