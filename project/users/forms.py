"""User blueprint forms."""

from flask_wtf import Form
from wtforms import(
    StringField,
    PasswordField,
)
from wtforms.validators import(
    InputRequired,
    Length,
    EqualTo
)


class RegisterForm(Form):
    """User Registration."""

    name = StringField(
        'Username',
        validators=[
            InputRequired(),
            Length(min=6, max=25)
        ]
    )
    email = StringField(
        'Email',
        validators=[
            InputRequired(),
            Length(min=6, max=40)
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            Length(min=6, max=40)
        ]
    )
    confirm = PasswordField(
        'Repeat Password',
        validators=[
            InputRequired(),
            EqualTo('password', message='Passwords must match')
        ]
    )


class LoginForm(Form):
    """User Login."""

    name = StringField(
        'Username',
        validators=[InputRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[InputRequired()]
    )
