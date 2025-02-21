import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key'
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('SQLALCHEMY_DATABASE_URI') or 
        'sqlite:///' + os.path.join(basedir, 'app.db')
    )
    POSTS_PER_PAGE = 30
