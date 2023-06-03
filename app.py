from flask import Flask, render_template, url_for, redirect, flash
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = '31258776c638a3aa4c4cd33912a9aec2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

tasks = [
    {
        'id': 1,
        'title': 'Msid projekt',
        'description': 'Analiza danych',
        'deadline': datetime(2023, 6, 3, 12, 0, 0)
    },
    {
        'id': 2,
        'title': 'Kolokwium linux',
        'description': 'Koncowy test u dr Chudzika',
        'deadline': datetime(2023, 6, 10, 9, 0, 0)
    }
]

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    tasks = db.relationship('Task', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.DateTime)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Task('{self.title}', '{self.deadline}')"



@app.route("/hello")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/hello/<name>')
def hello_name(name):
    return f"<p>Hello, {name}!</p>"

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', tasks=db.session.query(Task).all())

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if db.session.query(User).filter_by(username=form.username.data).first():
            flash('Użytkownik o podanej nazwie już istnieje', 'danger')
        elif db.session.query(User).filter_by(email=form.email.data).first():
            flash('Użytkownik o podanym adresie email już istnieje', 'danger')
        else:
            user = User(username=form.username.data, email=form.email.data, password=bcrypt.generate_password_hash(form.password.data).decode('utf-8'))
            #user = User(username="Domini", email="domini@blog.com", password="pass")
            db.session.add(user)
            db.session.commit()
            flash(f'Utworzono konto dla użytkownika {form.username.data}! Teraz możesz się zalogować.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data): 
            login_user(user, remember=form.remember.data)
            flash('Zalogowano', 'success')
            return redirect(url_for('home'))
        else:
            flash('Logowanie nie powiodło się. Sprawdź email i hasło.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
