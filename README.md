# Hi there

This is a Web chat app for the course B/S software design.

The frontend is based on Semantic UI. The backend is based on Flask and SQLAlchemy. What makes online chatting possbile is Socket.IO and @miguelgrinberg's Flask-SocketIO.

# Screenshots

This is the main page:

![main](screenshots/main.png)

# Dependencies

To get this app running, you have to install the following dependencies:

- python2
- virtualenvwrapper
- mysql
- redis

# Set up

## create virtualenv

First, create a virtualenv using `mkvirtualenv` command. For example, 


```
mkvirtualenv chat
cd ChatApp
pip install -r requirements.txt
```

## create mysql user and database

Open `config.py`, create a mysql user, and a database, as defined in `SQLALCHEMY_DATABASE_URI`. Or you may change it to whatever you want.

For example:

```
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://chat:123456@localhost/chat'
```

This means that you need to create a user named `chat` with password `132456`, and create a database named `chat`.

```
python manage.py db migrate
python manage.py db upgrade
```

By now your database is created.

## set up redis & celery

Open another terminal tab and `cd ChatApp`, then 

```
workon chat
celery worker -A chatapp.celery_worker.celery --loglevel=info
```

Open another terminal tab and run redis, for example, `redis-server`. Make sure your redis server port matches the port defined in `config.py`.

## finally

```
python manage.py run
```

visit `localhost:5000` and you can see the page.