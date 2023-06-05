import secrets, os
from PIL import Image
from flask import Flask, render_template, url_for, redirect, flash, request, abort
from forms import RegistrationForm, LoginForm, UpdateAccountForm, TaskForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from notifications import show_one_hour_left_notification

app = Flask(__name__)
app.config['SECRET_KEY'] = '31258776c638a3aa4c4cd33912a9aec2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Musisz się zalogować, aby skorzystać z tej funkcjonalności"
login_manager.login_message_category = 'info'

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
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
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
    if current_user.is_authenticated:
        return render_template('home.html', tasks=Task.query.filter_by(user_id=current_user.id).order_by(Task.deadline.asc()))
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Użytkownik o podanej nazwie już istnieje', 'danger')
        elif User.query.filter_by(email=form.email.data).first():
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
            next_page = request.args.get('next')
            flash('Zalogowano', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Logowanie nie powiodło się. Sprawdź email i hasło.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_picture.filename)
    picture_filename = random_hex+file_extension
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
    output_size = (125, 125)
    resized_picture = Image.open(form_picture)
    resized_picture.thumbnail(output_size)
    resized_picture.save(picture_path)
    return picture_filename

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.username.data != current_user.username and User.query.filter_by(username=form.username.data).first():
            flash('Użytkownik o podanej nazwie już istnieje', 'danger')
        elif form.email.data != current_user.email and User.query.filter_by(email=form.email.data).first():
            flash('Użytkownik o podanym adresie email już istnieje', 'danger')
        else:
            current_user.username = form.username.data
            current_user.email = form.email.data
            if form.picture.data:
                current_user.image_file = save_picture(form.picture.data)
            db.session.commit()
            flash('Dane zaktualizowno pomyślnie', 'success')
            return redirect(url_for('account'))
        
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename=f'profile_pics/{current_user.image_file}')
    return render_template('account.html', title='Account', image_file=image_file, form=form) 

@app.route("/task/new", methods=['GET', 'POST'])
@login_required
def new_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, deadline=form.deadline.data, description=form.description.data, user_id=current_user.id)
        #datetime.strptime(form.deadline.data, '%Y-%m-%d %H:%M:%S')
        db.session.add(task)
        db.session.commit()
        flash('Zadanie zostało dodane!', 'success')
        return redirect(url_for('home'))
    return render_template('create_task.html', title='Nowe zadanie', form=form, legend='Nowe zadanie')

@app.route("/task/<int:task_id>")
def task(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('task.html', title=task.title, task=task)

@app.route("/task/<int:task_id>/update", methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)
    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.deadline = form.deadline.data
        db.session.commit()
        flash('Zaktualizowałeś pomyślnie zadanie!', 'success')
        return redirect(url_for('task', task_id=task.id))
    elif request.method == 'GET':
        form.title.data = task.title
        form.description.data = task.description
        form.deadline.data = task.deadline
        print(task.deadline)
    return render_template('create_task.html', title='Aktualizuj zadanie',
                           form=form, legend='Aktualizuj zadanie')

@app.route("/task/<int:task_id>/delete", methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)
    db.session.delete(task)
    db.session.commit()
    flash('Zadanie zostało usunięte!', 'success')
    return redirect(url_for('home'))

@app.route('/send-notification', methods=['POST'])
def send_notification():
    show_one_hour_left_notification()
    return 'OK'

if __name__ == "__main__":
    app.run(debug=True)
