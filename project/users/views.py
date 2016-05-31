"""Users Blueprint."""

from functools import wraps
from flask import (
    Blueprint,
    flash,
    redirect,
    request,
    render_template,
    session,
    url_for,
)
from sqlalchemy.exc import IntegrityError

# What does the . in .forms do?
from .forms import RegisterForm, LoginForm
from project import db, bcrypt
from project.models import User


# config


users_blueprint = Blueprint('users', __name__)


# helper functions


def login_required(test):
    """Wrapper to require login."""
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('users.login'))
    return wrap


# route handlers


@users_blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('role', None)
    session.pop('name', None)
    flash('Peace!')
    return redirect(url_for('users.login'))


@users_blueprint.route('/', methods=['GET', 'POST'])
def login():
    """Login."""
    error = None
    form = LoginForm(request.form)

    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(name=form.name.data).first()

            if user is not None and bcrypt.check_password_hash(
                    user.password, form.password.data):
                session['logged_in'] = True
                session['user_id'] = user.id
                session['role'] = user.role
                session['name'] = user.name
                flash("Welcome, {0}".format(user.name))
                return redirect(url_for('tasks.tasks'))
            else:
                error = 'Invalid credentials.  Please try again.'
        else:
            error = 'Both fields are required.'

    return render_template(
        'login.html',
        form=form,
        error=error
    )


@users_blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    """User registration."""
    error = None
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        new_user = User(
            form.name.data,
            form.email.data,
            bcrypt.generate_password_hash(form.password.data)
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Thanks for registering, {0}".format(new_user.name))
            return redirect(url_for('users.login'))
        except IntegrityError:
            error = "That username and/or email already exists."

    return render_template(
        'register.html',
        form=form,
        error=error
    )
