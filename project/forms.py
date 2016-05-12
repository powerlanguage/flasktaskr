from flask_wtf import Form
from wtforms import(
    StringField,
    DateField,
    IntegerField,
    SelectField,
    PasswordField,
)
from wtforms.validators import(
    InputRequired,
    Length,
    EqualTo
)


class AddTaskForm(Form):
    task_id = IntegerField()
    name = StringField('Task Name', validators=[InputRequired()])
    due_date = DateField(
        'Date Due (mm/dd/yyy)',
        validators=[InputRequired()],
        format='%m/%d/%Y'
    )
    priority = SelectField(
        'Priority',
        validators=[InputRequired()],
        choices=[
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
            ('7', '7'),
            ('8', '8'),
            ('9', '9'),
            ('10', '10')
        ]
    )
    status = IntegerField('Status')


class RegisterForm(Form):
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
    name = StringField(
        'Username',
        validators=[InputRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[InputRequired()]
    )
