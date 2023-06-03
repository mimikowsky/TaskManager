from flask import Flask, render_template, url_for, redirect, flash
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '31258776c638a3aa4c4cd33912a9aec2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

tasks = [
    {
        'title': 'Msid projekt',
        'description': 'Analiza danych',
        'date': '14.06.2023'
    },
    {
        'title': 'Kolokwium linux',
        'description': 'Koncowy test u dr Chudzika',
        'date': '13.06.2023'
    }
]

class User(db.Model):
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
    return render_template('home.html', tasks=tasks)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if db.session.query(User).filter_by(username=form.username.data).first():
            flash('Użytkownik o podanej nazwie już istnieje', 'danger')
        elif db.session.query(User).filter_by(email=form.email.data).first():
            flash('Użytkownik o podanym adresie email już istnieje', 'danger')
        else:
            user = User(username=form.username.data, email=form.email.data, password=form.password.data)
            #user = User(username="Domini", email="domini@blog.com", password="pass")
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        #if form.email.data == 'admin@blog.com' and form.password.data == 'password':
        user = db.session.query(User).filter_by(email=form.email.data).first()
        print(user)
        if user and user.password == form.password.data: 
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


if __name__ == "__main__":
    app.run(debug=True)
