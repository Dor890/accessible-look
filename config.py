import os


class Config:
    SECRET_KEY = os.environ.get('DB_SECRET_KEY') or 'dorsafi123'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
