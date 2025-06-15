import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'yourgmail@gmail.com'  # your actual Gmail
    MAIL_PASSWORD = 'abcd efgh ijkl mnop'  # app password from Google
    MAIL_DEFAULT_SENDER = 'yourgmail@gmail.com'  # must match username
