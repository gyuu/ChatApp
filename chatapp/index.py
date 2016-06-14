from flask import (
    Blueprint,
    render_template,
    request,
)


indexbp = Blueprint('index', __name__)


@indexbp.route('/', methods=['GET'])
def index():
    return render_template('login.html')
