from flask import Blueprint, render_template

indexbp = Blueprint('index', __name__)

from . import socketio


@indexbp.route('/', methods=['GET'])
def index():
    return render_template('login.html')
