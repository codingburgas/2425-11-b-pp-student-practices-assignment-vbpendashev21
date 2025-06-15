from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import Email, Length, EqualTo
from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_wtf.file import FileField, FileRequired, FileAllowed

class PredictionForm(FlaskForm):
    temperature = FloatField('Температура (°C)', validators=[DataRequired()])
    condition = SelectField(
        'Атмосферни условия',
        choices=[
            ('Слънчево ☀️', 'Слънчево ☀️'),
            ('Облачно ☁️', 'Облачно ☁️'),
            ('Дъждовно 🌧️', 'Дъждовно 🌧️'),
            ('Снежно ❄️', 'Снежно ❄️'),
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Прогнозирай облекло')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired()])
    email = StringField('Имейл', validators=[DataRequired(), Email()])
    password = PasswordField('Парола', validators=[DataRequired()])
    confirm_password = PasswordField('Потвърди паролата', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Регистрация')


class EditProfileForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Нова парола (по избор)')
    submit = SubmitField('Запази промените')



class ImageUploadForm(FlaskForm):
    image = FileField('Изображение', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Само изображения!')
    ])
    submit = SubmitField('Анализирай изображението')

from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, StringField, SubmitField
from wtforms.validators import InputRequired

class PredictionForm(FlaskForm):
    temperature = FloatField('Temperature', validators=[InputRequired()])
    condition = SelectField('Condition', choices=[
        ('sunny', 'Sunny ☀️'),
        ('rain', 'Rain 🌧️'),
        ('snow', 'Snow ❄️')
    ])
    description = StringField('Description')
    ai_mode = SelectField('AI Mode', choices=[
        ('simple', 'Simple AI'),
        ('advanced', 'Advanced AI')
    ])
    submit = SubmitField('Predict')
