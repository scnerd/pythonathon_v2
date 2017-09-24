import flask
from flask import Flask, request, url_for, render_template
from urllib.parse import urlparse, urljoin
from flask_sqlalchemy import SQLAlchemy
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, login_required
from flask_wtf import FlaskForm
import json
from models import *
import forms
import logging
import os

login_manager = LoginManager()

nav = Nav()

@nav.navigation()
def mynavbar():
    return Navbar(
        'Pythonathon',
        View('Home', 'index'),
        View('Login', 'signin'),
        View('Questions', 'category_list'),
        View('Results', 'results_home')
    )

app = Flask(__name__)
db_path = 'pythonathon_data.db'
if os.path.exists(db_path):
    make_db = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pythonathon_data.db'
else:
    make_db = True
    logging.warning("Database {} not found, initializing a temporary empty database in memory")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

nav.init_app(app)
Bootstrap(app)
login_manager.init_app(app)

db = SQLAlchemy(app)
if make_db:
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


@app.route('/')
def index():
    return render_template('home_page.html')


@app.route('/signin', methods=['GET'])
def signin():
    login_form = forms.LoginForm()
    register_form = forms.RegistrationForm()
    return flask.render_template('login.html', login_form=login_form, register_form=register_form)


@app.route('/login', methods=['POST'])
def login():
    """Page to log in as a user"""
    form = forms.LoginForm(request.form)
    if form.validate() and form.user is not None:
        login_user(form.user, remember=True, fresh=True)
        next = request.args.get('next')
        if not is_safe_url(next):
            return flask.abort(400)
        return flask.redirect(next or flask.url_for('/index'))
    return flask.redirect(flask.url_for('/signin'))

login_manager.unauthorized_handler(login)


@app.route('/register', methods=['POST'])
def register():
    """Page to create a new user"""
    form = forms.RegistrationForm(request.form)
    if form.validate():
        user = User.query.filter(User.username == form.username.data).one_or_none()
        if user is not None:
            return flask.redirect(flask.url_for('/signin'))

        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.add(user)
        login_user(user, remember=True, fresh=True)

        next = request.args.get('next')
        if not is_safe_url(next):
            return flask.abort(400)
        return flask.redirect(next or flask.url_for('index'))
    return flask.redirect(flask.url_for('/signin'))


@app.route('/questions')
def category_list():
    """Return a page that lists all the available categories"""
    raise NotImplemented()


def _current_user():
    raise NotImplemented()


def _get_category(id_or_path):
    args = {'path': str(id_or_path)} if not id_or_path.isdigit() else {'id': int(id_or_path)}
    category = Category.query.filter_by(**args).one()

    user = _current_user()
    if category.requires and user not in category.requires.solvers:
        raise PermissionError("This user is not alloweed to access this category")
    return category


def _check_question(question, limit_category=None):
    user = _current_user()

    if limit_category:
        if question not in limit_category.questions:
            raise AttributeError("Question '{}' does not exist in category '{}'".format(question, limit_category))
        if limit_category.requires and user not in limit_category.requires.solvers:
            raise PermissionError("{} is not alloweed to access {}".format(user, limit_category))

    if question.requires and user not in question.requires.solvers:
        raise PermissionError("{} is not alloweed to access {}".format(user, question))
    return question


def _get_question(id_or_path, limit_category=None, skip_check=False):
    args = {'path': str(id_or_path)} if not id_or_path.isdigit() else {'id': int(id_or_path)}
    question = Question.query.filter_by(**args).one()

    if skip_check:
        return question
    return _check_question(question, limit_category)


@app.route('/questions/<category>')
@login_required
def question_list(category):
    """Return a page that lists all questions in a given category"""
    # Check availability for the current user
    category = _get_category(category)
    questions = [_check_question(q, category) for q in category.questions]
    raise NotImplemented()


@app.route('/questions/<category>/<question>')
@login_required
def question(category, question):
    """The category's not necessary, but gives nice tiering"""
    question = _get_question(question, _get_category(category))
    raise NotImplemented()


@app.route('/results')
def results_home():
    """Display overview of the current status of the hackathon, and links to specific results"""
    raise NotImplemented()


if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    app.run(debug=True)
