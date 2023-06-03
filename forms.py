from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired(), Length(min=4, max=20)])

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField('Potwierdź hasło', validators=[DataRequired(), EqualTo('password', message="Hasła różnią się.")])
    submit = SubmitField('Utwórz konto')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Hasło', validators=[DataRequired()])
    remember = BooleanField()
    submit = SubmitField('Zaloguj')