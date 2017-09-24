from pythonathon import app, db
from models import *
from argparse import ArgumentParser
import getpass

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('questions', help='Path to JSON list of questions to pre-load',
                        type=str, default=None)
    parser.add_argument('admin', help='Sets the admin password',
                        type=str, default=None)
    args = parser.parse_args()

    db.create_all()

    if args.questions is not None:
        import json
        # Expect [{category_kwargs, 'questions': [questions_kwargs]}]
        loaded = json.load(open(args.questions))
        categories = [Category(**{k: v for k, v in category.items() if k != 'questions'},
                               questions=[Question(**question) for question in category.get('questions', [])])
                      for category in loaded
        ]
        db.add_all(categories)

    admin_username = args.admin if args.admin is not None else getpass.getuser('Admin username: ').strip()
    admin_password = getpass.getpass('Admin password: ')

    db.add(User(username=admin_username, password=admin_password, is_admin=True))