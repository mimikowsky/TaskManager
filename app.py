import secrets, os
from PIL import Image
from flask import Flask, render_template, url_for, redirect, flash, request, abort, jsonify
from forms import RegistrationForm, LoginForm, UpdateAccountForm, TaskForm, RequestResetForm, ResetPasswordForm, CategoryForm
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from notifications import show_notification
from task_to_google import add_to_calendar
import sys
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import and_

app = Flask(__name__)
app.config['SECRET_KEY'] = '31258776c638a3aa4c4cd33912a9aec2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Musisz się zalogować, aby skorzystać z tej funkcjonalności"
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'taskmanagerdk@gmail.com'
app.config['MAIL_PASSWORD'] = 'ioyujmjziljlbmfe'
mail = Mail(app)

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
    categories = db.relationship('Category', backref='owner', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
    def get_reset_token(self, expires_sec=18000):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
    

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.DateTime)
    description = db.Column(db.Text, nullable=False)
    deadline_reminder = db.Column(db.Boolean, nullable=False)
    one_hour_reminder = db.Column(db.Boolean, nullable=False)
    one_day_reminder = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    

    def __repr__(self):
        return f"Task('{self.title}', '{self.deadline}')"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tasks = db.relationship('Task', backref='type', lazy=True)


    def __repr__(self):
        return f"Category {self.name}"
    

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
        return render_template('home.html', tasks=Task.query.filter_by(user_id=current_user.id).order_by(Task.deadline.asc()), get_task_name=get_task_name,
                               categories = Category.query.filter_by(user_id=current_user.id).all())
    return redirect(url_for('login'))

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
            flash(f'Utworzono konto dla użytkownika {form.username.data}!', 'success')
            
            initilize_categories_for_user(user)
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
    deadline = request.args.get('deadline')
    try:
        print(deadline[:4], deadline[5:7], deadline[8:], file=sys.stderr)
        month = deadline[5:7]
        if month[0] == "0":
            month = month[1]
        deadline_dt = datetime(int(deadline[:4]), int(month), int(deadline[8:]), 12, 0)
        
    except:
        pass
    form = TaskForm()

    categs = Category.query.filter_by(user_id=current_user.id).all()
    choices = [(category.id, category.name) for category in categs]
    form.category.choices = choices

    if deadline != None:
        form.deadline.data = deadline_dt
        
    if form.validate_on_submit():
        task = Task(title=form.title.data, deadline=form.deadline.data, description=form.description.data,
                    deadline_reminder=form.deadline_reminder.data, one_hour_reminder=form.one_hour_reminder.data,
                    one_day_reminder=form.one_day_reminder.data, user_id=current_user.id, category=form.category.data)
        #datetime.strptime(form.deadline.data, '%Y-%m-%d %H:%M:%S')
        db.session.add(task)
        db.session.commit()
        flash('Zadanie zostało dodane!', 'success')
        return redirect(url_for('home'))
   
    return render_template('create_task.html', title='Nowe zadanie', form=form, legend='Nowe zadanie', categories=Category.query.filter_by(user_id=current_user.id))

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
    
    categs = Category.query.filter_by(user_id=current_user.id).all()
    choices = [(category.id, category.name) for category in categs]
    form.category.choices = choices

    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.deadline = form.deadline.data
        task.deadline_reminder = form.deadline_reminder.data
        task.one_hour_reminder = form.one_hour_reminder.data
        task.one_day_reminder = form.one_day_reminder.data
        task.category = form.category.data
        db.session.commit()
        flash('Zadanie zaktualizowano pomyślnie!', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.title.data = task.title
        form.description.data = task.description
        form.deadline.data = task.deadline
        form.deadline_reminder.data = task.deadline_reminder
        form.one_hour_reminder.data = task.one_hour_reminder
        form.one_day_reminder.data = task.one_day_reminder
        form.category.data = task.category
    return render_template('create_task.html', title='Aktualizuj zadanie',
                           form=form, legend='Aktualizuj zadanie', categories=Category.query.filter_by(user_id=current_user.id))

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
    data = request.json
    task_id = data.get('task_id')
    notification_number = int(data.get('notification_number'))
    task = Task.query.filter_by(id=task_id).first()
    if notification_number == 0:
        show_notification(task, f"{task.title}", f"Upłynął termin: {task.title}")
    elif notification_number == 1:
        show_notification(task, "Została godzina!", f"Została godzina do upływu terminu: {task.title}")
    elif notification_number == 2:
        show_notification(task, "Zostały 24 godziny!", f"Zostały 24 godziny do upływu terminu: {task.title}")

    return 'OK'

@app.route('/<int:task_id>/calendar')
def send_to_calendar(task_id):
    if current_user.is_authenticated:
        task = Task.query.filter_by(id=task_id).first()
        if task.author == current_user:
            add_to_calendar(task)

    return redirect(url_for('home'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Zmiana hasła TaskManager', sender="taskmanager@gmail.com", recipients=[user.email])
    msg.body = f'''Aby zmienić hasło, kliknij link: {url_for('reset_token', token=token, _external=True)} 
Jeżeli nie prosiłeś o wysłanie tego maila, po prostu zignoruj tego maila.
Żadne zmiany nie zostaną dokonane'''
    mail.send(msg)

@app.route("/reset_password", methods = ['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user == None:
            flash('Użytkownik o podanym adresie email nie istnieje', 'warning')
        else: 
            send_reset_email(user)
            flash('Wysłano maila z linkiem do strony zmiana hasła.', 'info')
            return redirect(url_for('login'))
    return render_template('reset_request.html', title='Resetuj hasło', form=form)

@app.route("/reset_password/<token>", methods = ['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Ten link jest już nieważny. Linki zmiany hasła ważne są przez 30 minut. Wygeneruj nowy.', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()
        flash(f'Hasło zostało zmienione. Możesz teraz się zalogować.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Resetuj hasło', form=form)

@app.route("/create_category", methods = ['GET', 'POST'])
@login_required
def create_category():

    form = CategoryForm()

    if form.validate_on_submit():
        #categories=Category.query.filter_by(name=form.name.data)
        if db.session.query(Category).filter_by(name=form.name.data, user_id=current_user.id).first() is not None:
            flash('Kategoria o tej nazwie juz istnieje!', 'warning')
        else:
            category = Category(name=form.name.data, user_id=current_user.id)
            db.session.add(category)
            db.session.commit()
            flash('Kategoria została dodana!', 'success')

        return redirect(url_for('home'))
    return render_template("create_category.html", form=form)
    
def get_task_name(id):
    cat = db.session.query(Category).filter_by(id = id).first()
    try:
        name = cat.name
    except:
        name = "Brak"
    return name


def initilize_categories_for_user(user):
    """ only use for new registered user (so with no categories)"""
    cat1 = Category(name="Studia", user_id=user.id)
    cat2 = Category(name="Praca", user_id=user.id)
    cat3 = Category(name="Dom", user_id=user.id)
    db.session.add(cat1)
    db.session.add(cat2)
    db.session.add(cat3)
    db.session.commit()

@app.route('/filtruj', methods=['POST'])
@login_required
def ffilter_tasks():
    selected_categories = request.form.getlist('kategoria')
    selected_categories = [int(category) for category in selected_categories]
    
    category_filter = Task.category.in_(selected_categories)
    tasks=Task.query.filter_by(user_id=current_user.id).filter(category_filter).order_by(Task.deadline.asc())
    
    categs = Category.query.filter(Category.id.in_(selected_categories)).all()
    category_names = [category.name for category in categs]
    category_names_string = ', '.join(category_names)
    mess = f"Filtr kategorii: {category_names_string}"
    
    flash(mess, 'success')
    return render_template('home.html', tasks = tasks, get_task_name=get_task_name,
                               categories = Category.query.filter_by(user_id=current_user.id).all())

if __name__ == "__main__":
    app.run(debug=True)
