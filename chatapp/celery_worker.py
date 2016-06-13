#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from time import sleep
from . import celery, create_app
from .celeryconfig import celeryconfig


# celery needs a separate flask app instance.
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()

celery.conf.update(celeryconfig)
