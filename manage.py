#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from chatapp import (
    create_app,
    db,
    socketio,
)

from chatapp.models import (
    User,
)


from flask.ext.script import (
    Manager,
    Shell,
)
from flask.ext.migrate import (
    Migrate,
    MigrateCommand
)


# test
# from tests.register import payload
from tests.posts import show_post, sell_post

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(
        app=app, db=db,
        User=User,
        # test upload post
        show_post=show_post, sell_post=sell_post,
    )


@manager.command
def run():
    print 'socketio server running'
    socketio.run(app, debug=True)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
