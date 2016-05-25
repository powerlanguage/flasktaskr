"""Public docstring."""

from functools import wraps

from flask import (
    flash,
    Flask,
    redirect,
    request,
    render_template,
    session,
    url_for,
)
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from forms import AddTaskForm, RegisterForm, LoginForm
import datetime

# config

app = Flask(__name__)
app.config.from_object('_config')
db = SQLAlchemy(app)

from models import Task, User


# helper functions


def login_required(test):
    """Wrapper to require login."""
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('login'))
    return wrap


def open_tasks():
    """Return open tasks."""
    return db.session.query(Task) \
        .filter_by(status='1').order_by(Task.due_date.asc())


def closed_tasks():
    """Return closed tasks."""
    return db.session.query(Task) \
        .filter_by(status='0').order_by(Task.due_date.asc())


# route handlers


@app.route('/logout/')
@login_required
def logout():
    """Logout."""
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('role', None)
    flash('Peace!')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def login():
    """Login."""
    error = None
    form = LoginForm(request.form)

    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(name=form.name.data).first()

            if user is not None and user.password == form.password.data:
                session['logged_in'] = True
                session['user_id'] = user.id
                session['role'] = user.role
                flash("Welcome, {0}".format(user.name))
                return redirect(url_for('tasks'))
            else:
                error = 'Invalid credentials.  Please try again.'
        else:
            error = 'Both fields are required.'

    return render_template(
        'login.html',
        form=form,
        error=error
    )


@app.route('/register/', methods=['GET', 'POST'])
def register():
    """User registration."""
    error = None
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        new_user = User(
            form.name.data,
            form.email.data,
            form.password.data
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Thanks for registering, {0}".format(new_user.name))
            return redirect(url_for('login'))
        except IntegrityError:
            error = "That username and/or email already exists."

    return render_template(
        'register.html',
        form=form,
        error=error
    )


@app.route('/tasks/')
@login_required
def tasks():
    """Display open and closed tasks."""
    return render_template(
        'tasks.html',
        form=AddTaskForm(request.form),
        open_tasks=open_tasks(),
        closed_tasks=closed_tasks()
    )


@app.route('/add/', methods=['POST'])
@login_required
def new_task():
    """Add a new task."""
    form = AddTaskForm(request.form)
    if form.validate_on_submit():
        new_task = Task(
            form.name.data,
            form.due_date.data,
            form.priority.data,
            datetime.datetime.utcnow(),
            '1',
            session['user_id']
        )
        db.session.add(new_task)
        db.session.commit()
        flash("{0} was successfully posted. Thanks.".format(new_task.name))
    return render_template(
        'tasks.html',
        form=form,
        open_tasks=open_tasks(),
        closed_tasks=closed_tasks()
    )


@app.route('/delete/<int:task_id>/')
@login_required
def delete_task(task_id):
    """Delete a task by id."""
    task = Task.query.filter_by(task_id=task_id)

    if task.first().user_id == session['user_id'] \
            or session['role'] == 'admin':
        # have to store the task name for the flash before we delete it
        task_name = task.first().name
        task.delete()
        db.session.commit()
        flash("{0} was deleted. Nice".format(task_name))
    else:
        flash("You can only delete tasks that belong to you.")
    return redirect(url_for('tasks'))


@app.route('/complete/<int:task_id>/')
@login_required
def complete_task(task_id):
    """Complete a task by id."""
    task = Task.query.filter_by(task_id=task_id)

    if task.first().user_id == session['user_id'] \
            or session['role'] == 'admin':
        task.update({"status": "0"})
        db.session.commit()
        flash("{0} was completed. Nice".format(task.first().name))
    else:
        flash("You can only update tasks that belong to you.")

    return redirect(url_for('tasks'))


# def flash_errors(form):
#     """Flash errors in forms."""
#     for field, errors in form.errors.items():
#         for error in errors:
#             flash(
#                 "Error in the {} field - {} error".format(
#                     getattr(form, field).label.text,
#                     error
#                 )
#             )
