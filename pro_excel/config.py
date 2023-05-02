import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    flask_ENV='development'
    DEBUG=True
    SECRET_KEY = '_5#y2L"F4Q8zxec]/'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'book_manage.sqlite')
    UPLOAD_FOLDER = os.path.join(basedir, 'upload\\')
    # PERMANENT_SESSION_LIFETIME = timedelta(days=7)