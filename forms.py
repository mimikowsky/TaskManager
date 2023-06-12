from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed 
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NoneOf
from wtforms.fields import DateTimeField

class RegistrationForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField('Potwierdź hasło', validators=[DataRequired(), EqualTo('password', message="Hasła różnią się.")])
    submit = SubmitField('Utwórz konto')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Hasło', validators=[DataRequired()])
    remember = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj')

class UpdateAccountForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Zmień zdjęcie profilowe', validators=[FileAllowed(['jpg', 'png'], message="Akceptowane rozszerzenia: jpg, png")])
    submit = SubmitField('Zaktualizuj')

class TaskForm(FlaskForm):
    title = StringField('Tytuł', validators=[DataRequired()])
    description = TextAreaField('Opis', validators=[DataRequired()])
    deadline = DateTimeField('Termin', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    deadline_reminder = BooleanField('O godzinie terminu')
    one_hour_reminder = BooleanField('Godzinę przed')
    one_day_reminder = BooleanField('Dzień przed')
    category = SelectField('Wybierz kategorię:', coerce=int, validators=[DataRequired()], choices=[])
    submit = SubmitField('Zatwierdź')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Wyślij maila z linkiem do strony zmiany hasła')
  
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Hasło', validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField('Potwierdź hasło', validators=[DataRequired(), EqualTo('password', message="Hasła różnią się.")])
    submit = SubmitField('Zmień hasło')

class CategoryForm(FlaskForm):
    name = StringField('Stwórz kategorię')
    submit = SubmitField('Dodaj')