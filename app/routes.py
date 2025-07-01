import os
import io
from flask import render_template, redirect, url_for, flash, request, Response, abort, current_app, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from functools import wraps
from app.models import db, User, Survey, Prediction
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ImageUploadForm, PredictionForm
from flask import Blueprint
from app.linear_model import TinyOutfitNet
from app import login_manager
from urllib.parse import urlparse

main_bp = Blueprint('main', __name__)
model = TinyOutfitNet()

# Outfit translations for Bulgarian UI
OUTFIT_TRANSLATIONS_BG = {
    "T-shirt + Jeans": "Тениска + Дънки",
    "Sweatshirt + Jeans": "Суитшърт + Дънки",
    "Winter coat": "Зимно яке",
    "Crop top + Shorts": "Къс топ + Къси панталони",
    "Raincoat": "Дъждобран",
    "Shorts + T-shirt": "Къси панталони + Тениска",
    "Jacket + Jeans": "Яке + Дънки",
    "Coat + Warm clothes": "Палто + Топли дрехи",
    "Hooded raincoat + Jeans": "Дъждобран с качулка + Дънки",
    # Add other possible outputs if needed
}

def translate_outfit(outfit, lang):
    if lang == 'bg':
        return OUTFIT_TRANSLATIONS_BG.get(outfit, outfit)
    return outfit

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return wrapper

@main_bp.route("/", methods=["GET", "POST"])
@login_required
def image_index():
    form = PredictionForm()
    lang = session.get('lang', 'bg')
    return render_template("index.html", form=form)

@main_bp.route("/predict_outfit", methods=["POST"])
@login_required
def predict_outfit():
    form = PredictionForm()
    lang = session.get('lang', 'bg')
    if form.validate_on_submit():
        try:
            temp = form.temperature.data
            condition = form.condition.data
            description = form.description.data
            is_public = form.is_public.data

            outfit, probs = model.predict(temp, condition)
            confidence = max(probs)
            outfit_display = translate_outfit(outfit, lang)

            prediction = Prediction(
                user_id=current_user.id,
                temperature=temp,
                condition=condition,
                description=description,
                predicted_outfit=outfit,
                confidence=confidence,
                is_public=is_public
            )
            db.session.add(prediction)
            db.session.commit()

            return render_template("index.html",
                                   form=PredictionForm(),
                                   outfit=outfit_display,
                                   confidence=confidence,
                                   prediction_id=prediction.id)
        except Exception as e:
            current_app.logger.error(f"Prediction failed: {str(e)}")
            flash("Prediction failed. Please try again.", "error")
    else:
        current_app.logger.warning(f"Form validation failed: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "error")
    return render_template("index.html", form=form)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.image_index'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.image_index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()
        if existing_user:
            flash("Потребителското име или имейл вече съществуват.", "danger")
            return render_template("register.html", form=form)
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Регистрацията е успешна! Провери имейла си за потвърждение.")
        return redirect(url_for("main.login"))
    return render_template("register.html", form=form)

@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))

@main_bp.route("/set_language", methods=['GET', 'POST'])
def set_language():
    lang = request.args.get('lang', 'bg')
    session['lang'] = lang
    referrer = request.referrer
    if referrer:
        parsed = urlparse(referrer)
        if parsed.path.endswith('/predict_outfit'):
            return redirect(url_for('main.image_index'))
    return redirect(referrer or url_for('main.image_index'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main_bp.route("/my_predictions")
@login_required
def my_predictions():
    lang = session.get('lang', 'bg')
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.timestamp.desc()).all()
    for p in predictions:
        p.predicted_outfit_display = translate_outfit(p.predicted_outfit, lang)
    return render_template('my_predictions.html', predictions=predictions)

@main_bp.route('/public_predictions')
@login_required
def public_predictions():
    lang = session.get('lang', 'bg')
    predictions = Prediction.query.filter_by(is_public=True).order_by(Prediction.timestamp.desc()).all()
    for p in predictions:
        p.predicted_outfit_display = translate_outfit(p.predicted_outfit, lang)
        if hasattr(p, "user_id"):
            user = User.query.filter_by(id=p.user_id).first()
            p.username = user.username if user else "Unknown"
    return render_template('public_predictions.html', predictions=predictions)

@main_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        if form.password.data:
            current_user.set_password(form.password.data)
        db.session.commit()
        flash("Профилът е обновен успешно.")
        return redirect(url_for("main.profile"))
    return render_template("profile.html", form=form)

@main_bp.route("/admin/users")
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template("admin_users.html", users=users)

@main_bp.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash("Не може да изтривате администратор.")
    else:
        db.session.delete(user)
        db.session.commit()
        flash("Потребителят е изтрит.")
    return redirect(url_for('main.admin_users'))

@main_bp.route("/admin/predictions")
@login_required
@admin_required
def admin_predictions():
    username = request.args.get("user")
    condition = request.args.get("condition")
    query = Prediction.query
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            query = query.filter_by(user_id=user.id)
    if condition:
        query = query.filter_by(condition=condition)
    predictions = query.order_by(Prediction.timestamp.desc()).all()
    users = User.query.all()
    return render_template("admin_predictions.html", predictions=predictions, users=users)

@main_bp.route("/submit_feedback", methods=["POST"])
@login_required
def submit_feedback():
    from app.models import Feedback
    prediction_id = request.form.get("prediction_id")
    rating = request.form.get("rating")
    comment = request.form.get("comment")
    if prediction_id and rating:
        feedback = Feedback(
            prediction_id=int(prediction_id),
            rating=int(rating),
            comment=comment
        )
        db.session.add(feedback)
        db.session.commit()
        flash("Благодарим за отзива!")
    return redirect(url_for("main.image_index"))
