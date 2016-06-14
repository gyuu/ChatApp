# -*- coding: utf-8 -*-
import os

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])
UPLOAD_FOLDER = os.path.join(
    os.path.dirname(
        os.path.split(
            os.path.abspath(__file__)
        )[0]
    ), 'static/img/')


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
