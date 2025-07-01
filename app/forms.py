from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from flask_wtf.file import FileField, FileRequired, FileAllowed

class PredictionForm(FlaskForm):
    temperature = FloatField('Temperature', validators=[DataRequired()])
    condition = SelectField('Condition', validators=[DataRequired()])
    description = StringField('Description')
    is_public = BooleanField('Make prediction public')
    submit = SubmitField('Predict')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lang = session.get('lang', 'bg')
        if lang == 'bg':
            self.condition.choices = [
                ('sunny', 'Слънчево ☀️'),
                ('rain', 'Дъжд 🌧️'),
                ('snow', 'Сняг ❄️'),
            ]
        else:
            self.condition.choices = [
                ('sunny', 'Sunny ☀️'),
                ('rain', 'Rain 🌧️'),
                ('snow', 'Snow ❄️'),
            ]

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password')
    ])
    submit = SubmitField('Register')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('New password (optional)')
    submit = SubmitField('Save changes')

class ImageUploadForm(FlaskForm):
    image = FileField('Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    submit = SubmitField('Analyze image')
