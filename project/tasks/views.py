"""Tasks Blueprint."""

from functools import wraps
import datetime

from flask import (
    Blueprint,
    flash,
    redirect,
    request,
    render_template,
    session,
    url_for,
)

from .forms import AddTaskForm
from project import db
from project.models import Task


# config


tasks_blueprint = Blueprint('tasks', __name__)


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


def open_tasks():
    """Return open tasks."""
    return db.session.query(Task) \
        .filter_by(status='1').order_by(Task.due_date.asc())


def closed_tasks():
    """Return closed tasks."""
    return db.session.query(Task) \
        .filter_by(status='0').order_by(Task.due_date.asc())


# route handlers

@tasks_blueprint.route('/tasks/')
@login_required
def tasks():
    """Display open and closed tasks."""
    return render_template(
        'tasks.html',
        form=AddTaskForm(request.form),
        open_tasks=open_tasks(),
        closed_tasks=closed_tasks(),
    )


@tasks_blueprint.route('/add/', methods=['POST'])
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
        closed_tasks=closed_tasks(),
    )


@tasks_blueprint.route('/delete/<int:task_id>/')
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
    return redirect(url_for('tasks.tasks'))


@tasks_blueprint.route('/complete/<int:task_id>/')
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

    return redirect(url_for('tasks.tasks'))
