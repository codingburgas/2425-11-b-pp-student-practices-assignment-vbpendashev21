from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config
from flask import Flask, render_template


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_message = None  # disable auto flash
mail = Mail()  # ✅ required by app.email

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # Already included ✅

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    # ✅ Register error handlers here
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    return app


