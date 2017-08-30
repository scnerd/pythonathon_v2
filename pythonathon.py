from flask import Flask
import json
from .models import *

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/login')
def login():
    """Page to log in as a user, or create a new user"""


@app.route('/questions')
def category_list():
    """Return a page that lists all the available categories"""
    raise NotImplemented()


def _current_user():
    raise NotImplemented()


def _get_category(id_or_path):
    args = {'path': str(id_or_path)} if not id_or_path.isdigit() else {'id': int(id_or_path)}
    category = db.query(Category).filter_by(**args).one()

    user = _current_user()
    if category.requires and user not in category.requires.solvers:
        raise PermissionError("This user is not alloweed to access this category")
    return category


def _check_question(question, limit_category=None):
    user = _current_user()

    if limit_category
        if question not in limit_category.questions:
            raise AttributeError("Question '{}' does not exist in category '{}'".format(question, limit_category))
        if limit_category.requires and user not in limit_category.requires.solvers:
            raise PermissionError("{} is not alloweed to access {}".format(user, limit_category))

    if question.requires and user not in question.requires.solvers:
        raise PermissionError("{} is not alloweed to access {}".format(user, question))
    return question


def _get_question(id_or_path, limit_category=None, skip_check=False):
    args = {'path': str(id_or_path)} if not id_or_path.isdigit() else {'id': int(id_or_path)}
    question = db.query(Question).filter_by(**args).one()

    if skip_check:
        return question
    return _check_question(question, limit_category)


@app.route('/questions/<category>')
def question_list(category):
    """Return a page that lists all questions in a given category"""
    # Check availability for the current user
    category = _get_category(category)
    questions = [_check_question(q, category) for q in category.questions]
    raise NotImplemented()


@app.route('/questions/<category>/<question>')
def question(category, question):
    """The category's not necessary, but gives nice tiering"""
    question = _get_question(question, _get_category(category))
    raise NotImplemented()


@app.route('/results')
def results_home():
    """Display overview of the current status of the hackathon, and links to specific results"""
    raise NotImplemented()


if __name__ == '__main__':
    app.run(host='0.0.0.0')
