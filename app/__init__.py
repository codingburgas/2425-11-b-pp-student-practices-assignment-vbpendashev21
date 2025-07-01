from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from config import Config
from app.models import db  # 👈 това идва от models.py, където е db = SQLAlchemy()

login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)  # 👈 важно!
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = 'main.login'

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    @app.errorhandler(404)
    def not_found(e): return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(e): return render_template("403.html"), 403

    return app











