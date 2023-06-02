from flask import Flask, render_template, url_for, redirect, flash
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '31258776c638a3aa4c4cd33912a9aec2'

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
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


if __name__ == "__main__":
    app.run(debug=True)
