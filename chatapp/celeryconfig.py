#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import timedelta

celeryconfig = {

    # 'CELERY_RESULT_BACKEND': 'redis://localhost:6379/0',

    'CELERY_IMPORTS': ('tagbook.tasks', ),

    'CELERYBEAT_SCHEDULE': {
        # 'remove_offline_users': {
        #     'task': 'remove_expired_users',
        #     'schedule': timedelta(seconds=300),
        # },
        # 'ping_all_users': {
        #     'task': 'ping_all_users',
        #     'schedule': timedelta(seconds=240),
        # }
    }

}
