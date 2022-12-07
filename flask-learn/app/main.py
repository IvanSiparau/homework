from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
import pdfkit

app = Flask(__name__, template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '2193392i339&(*#(*#(*98290329))*)(#)(^$#^#%&$&^#BKJBCKJSBCKJjnfjnffjnjfKJWKJXKJNSXJNWLKLKCLKWNCJKWN'
db = SQLAlchemy()
db.init_app(app)
login_manager = LoginManager(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=True, nullable=False)


class DataUser(db.model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
@login_required
def index():
    return render_template('index.html', title="main")


@app.route("/download")
@login_required
def dowload_page():
    pdfkit.from_url('/', 'out.pdf')
    return render_template('index.html', title="main")


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        if login and password:
            user = User.query.filter_by(login=login).first()
            if request.method == 'POST':
                if user and user.password == password:
                    login_user(user)
                    return redirect(url_for('index'))
                else:
                    flash('Login or password is not correct')
        else:
            flash('Please fill login and password fields')
    return render_template('login.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    if request.method == 'POST':
        if login and password and password2:
            if password != password2:
                flash('Passwords are not equal!')
            else:
                new_user = User(login=login, password=password)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('index'))
        else:
            flash('Please, fill all fields!')
    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401 or response.status_code == 404:
        return redirect(url_for('login_page'))
    return response
