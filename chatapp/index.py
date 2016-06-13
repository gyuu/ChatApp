from flask import Blueprint, render_template

indexbp = Blueprint('index', __name__)


@indexbp.route('/', methods=['GET'])
def index():
    return render_template('login.html')


# @indexbp.route('/chat', methods=['GET'])
# def chat():
#     return render_template('chat.html')
