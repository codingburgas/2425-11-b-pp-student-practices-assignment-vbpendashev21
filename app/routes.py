import os
import io
from flask import render_template, redirect, url_for, flash, request, Response, abort, current_app, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from functools import wraps
import matplotlib.pyplot as plt
from app.models import Prediction
from app.forms import PredictionForm
from app import db, login_manager
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ImageUploadForm
from app.models import User, Survey
from flask import Blueprint
from app.simple_model import SimpleOutfitClassifier

main_bp = Blueprint('main', __name__)
model = SimpleOutfitClassifier()
try:
    model.load()
except FileNotFoundError:
    print("⚠️ model_weights.json not found — using untrained model.")

# 🔐 Admin-only decorator
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return wrapper

# 🧠 Main index page with prediction form
@main_bp.route("/", methods=["GET", "POST"])
@login_required
def image_index():
    form = PredictionForm()
    return render_template("index.html", form=form)

@main_bp.route("/predict_outfit", methods=["POST"])
@login_required
def predict_outfit():
    temp = float(request.form["temperature"])
    condition = request.form["condition"]
    description = request.form.get("description")
    ai_mode = request.form.get("ai_mode", "simple")  # Default to simple mode

    # Decide which model to use
    if ai_mode == "advanced":
        from app.advanced_model import AdvancedOutfitModel
        outfit_model = AdvancedOutfitModel()
    else:
        outfit_model = model  # Default simple model

    # Make prediction
    outfit, probs = outfit_model.predict(temp, condition)

    # Save to database
    prediction = Prediction(
        user_id=current_user.id,
        temperature=temp,
        condition=condition,
        description=description,
        predicted_outfit=outfit,
        confidence=max(probs)
    )
    db.session.add(prediction)
    db.session.commit()

    return render_template("index.html", outfit=outfit, confidence=max(probs), prediction_id=prediction.id)

# 🔑 Login
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

# 📝 Register
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

        #send_confirmation_email(user)
        flash("Регистрацията е успешна! Провери имейла си за потвърждение.")
        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)



# 🔐 Logout
@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))



# 📊 My Surveys
@main_bp.route("/my_surveys")
@login_required
def my_surveys():
    surveys = Survey.query.filter_by(user_id=current_user.id).order_by(Survey.timestamp.desc()).all()
    return render_template("my_surveys.html", surveys=surveys)

# 📈 Survey chart
@main_bp.route("/my_surveys_plot")
@login_required
def my_surveys_plot():
    surveys = Survey.query.filter_by(user_id=current_user.id).order_by(Survey.timestamp).all()
    if not surveys:
        return "No survey data", 404
    dates = [s.timestamp for s in surveys]
    temps = [s.temperature for s in surveys]
    plt.figure(figsize=(8, 4))
    plt.plot(dates, temps, marker='o', linestyle='-', color='blue')
    plt.title("Температура при попълнени анкети")
    plt.xlabel("Дата и час")
    plt.ylabel("Температура (°C)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    return Response(img.getvalue(), mimetype='image/png')



# 🙋‍♂️ Profile
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

# 👑 Admin: user management
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

# 🌐 Language toggle
@main_bp.route('/set_language/<lang>')
def set_language(lang):
    session['lang'] = lang
    return redirect(request.referrer or url_for('main.image_index'))

# 🔁 Login manager hook
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main_bp.route("/admin/predictions")
@login_required
@admin_required
def admin_predictions():
    from app.models import Prediction, User
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
    from app.models import Feedback, Prediction
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
