from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_message = None  # disable auto flash
mail = Mail()  # ✅ required by app.email

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # Make sure config includes mail settings

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)  # ✅ initialize Mail

    login_manager.login_view = 'main.login'

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app

