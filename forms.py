from wtforms import Form, BooleanField, StringField, PasswordField, validators, TextField, HiddenField
from flask import redirect, url_for


class RedirectForm(Form):
    next = HiddenField("Next")

    def __init__(self, *args, **kwargs):
        from pythonathon import get_redirect_target
        Form.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='index', **values):
        from pythonathon import is_safe_url, get_redirect_target
        if is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


class RegistrationForm(RedirectForm):
    username = StringField("Username", [validators.Length(min=4, max=32)])
    email = StringField("Email", [validators.Email()])
    password = PasswordField("Password", [validators.DataRequired(), validators.Length(min=8)])


class LoginForm(RedirectForm):
    username = StringField("Username", [validators.Length(min=4, max=32)])
    password = PasswordField("Password", [validators.DataRequired(), validators.Length(min=8)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        from models import User
        rv = super().validate()
        if not rv:
            return False

        user = (
            User.query
                .filter(User.username == self.username.data)
        ).one_or_none()

        if user is None:
            self.username.errors.append('Unknown username')
            return False

        if not user.password == self.password.data:
            self.password.errors.append('Incorrect password')
            return False

        self.user = user
        return True