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


# route handlers

@app.route('/logout/')
def logout():
    """Logout."""
    session.pop('logged_in', None)
    session.pop('user_id', None)
    flash('Peace!')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def login():
    """Login."""
    error = None
    form = LoginForm(request.form)

    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()

        if user is not None and user.password == form.password.data:
            session['logged_in'] = True
            session['user_id'] = user.id
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


@app.route('/register', methods=['GET', 'POST'])
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
        db.session.add(new_user)
        db.session.commit()
        flash("Thanks for registering, {0}".format(new_user.name))
        return redirect(url_for('login'))

    return render_template(
        'register.html',
        form=form,
        error=error
    )


@app.route('/tasks/')
@login_required
def tasks():
    """Display open and closed tasks."""
    open_tasks = db.session.query(Task) \
        .filter_by(status='1').order_by(Task.due_date.asc())

    closed_tasks = db.session.query(Task) \
        .filter_by(status='0').order_by(Task.due_date.asc())

    return render_template(
        'tasks.html',
        form=AddTaskForm(request.form),
        open_tasks=open_tasks,
        closed_tasks=closed_tasks
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
    else:
        flash(form.errors)

    return redirect(url_for('tasks'))


@app.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    """Delete a task by id."""
    task_name = Task.query.filter_by(task_id=task_id).first().name
    db.session.query(Task).filter_by(task_id=task_id).delete()
    db.session.commit()
    flash("{0} was deleted. Nice".format(task_name))
    return redirect(url_for('tasks'))


@app.route('/complete/<int:task_id>')
@login_required
def complete_task(task_id):
    """Complete a task by id."""
    task_name = Task.query.filter_by(task_id=task_id).first().name
    db.session.query(Task).filter_by(task_id=task_id).update({"status": "0"})
    db.session.commit()
    flash("{0} was completed. Nice".format(task_name))
    return redirect(url_for('tasks'))
