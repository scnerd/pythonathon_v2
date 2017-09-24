from pythonathon import db
import sqlalchemy_utils

Column = db.Column
Integer = db.Integer
String = db.String
DateTime = db.DateTime
Bool = db.Boolean
PasswordType = sqlalchemy_utils.PasswordType
ForeignKey = db.ForeignKey
relationship = db.relationship

class _NamedObj:
    def __repr__(self):
        return "<{} '{}'>".format(type(self).__name__, self.name)

    def __str__(self):
        return self.name


class Category(db.Model, _NamedObj):
    __tablename__ = 'category'

    id = Column(Integer, autoincrement=True, primary_key=True)
    path = Column(String, nullable=True)
    name = Column(String)
    requires = Column(Integer, ForeignKey('question.id'))

class Question(db.Model, _NamedObj):
    __tablename__ = 'question'

    id = Column(Integer, autoincrement=True, primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id', ondelete='CASCADE'))
    path = Column(String, nullable=True)
    name = Column(String)
    full_text = Column(String)
    hint = Column(String, default='')
    hint_cost = Column(Integer, default=0)
    answer = Column(String)
    case_sensitive = Column(Bool, default=True)
    points = Column(Integer, default=1)
    requires = Column(Integer, ForeignKey('question.id', ondelete='NULL'))

    category = relationship('Category', uselist=False, backref='questions', foreign_keys=[category_id])

class User(db.Model, _NamedObj):
    __tablename__ = 'user'

    id = Column(Integer, autoincrement=True)
    username = Column(String, primary_key=True)
    email = Column(String, nullable=True)
    password = Column(PasswordType)
    is_admin = Column(Bool, default=False)

    solved = relationship('Question', backref='solvers', secondary='solution')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_authenticated = False
        self.is_active = True
        self.is_anonymous = False

    @property
    def score(self):
        return sum(
            solution.question.score - int(solution.used_hint) * solution.question.hint_cost
            for solution in self.solutions
            if solution.success
        )

    @property
    def name(self):
        return self.username

    def get_id(self):
        return str(id).encode('utf8')


class Solution(db.Model):
    __tablename__ = 'solution'
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'question_id', name='solution_pk'),
    )

    user_id = Column(Integer, ForeignKey('user.id'))
    question_id = Column(Integer, ForeignKey('question.id'))
    submission = Column(String)
    timestamp = Column(DateTime)
    success = Column(Bool, default=False)
    used_hint = Column(Bool, default=False)

    user = relationship('User', uselist=False, backref='solutions')
    question = relationship('Question', uselist=False, backref='solutions')