"""API Blueprint."""


from functools import wraps
from flask import (
    redirect,
    flash,
    jsonify,
    session,
    url_for,
    Blueprint,
    make_response
)

from project import db
from project.models import Task

api_blueprint = Blueprint('api', __name__)


# Helper Methods


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('users.login'))
    return wrap


# Methods


@api_blueprint.route('/api/v1/tasks/')
def tasks():
    db_results = db.session.query(Task).limit(10).offset(0).all()
    json_results = []
    for result in db_results:
        data = {
            'task_id': result.task_id,
            'task name': result.name,
            'due date': str(result.due_date),
            'priority': result.priority,
            'posted date': str(result.posted_date),
            'status': result.status,
            'user id': result.user_id
        }
        json_results.append(data)
    return jsonify(items=json_results)


@api_blueprint.route('/api/v1/tasks/<int:id>')
def get_task(id):
    result = db.session.query(Task).filter_by(task_id=id).first()
    if result:
        json_result = {
            'task_id': result.task_id,
            'task name': result.name,
            'due date': str(result.due_date),
            'priority': result.priority,
            'posted date': str(result.posted_date),
            'status': result.status,
            'user id': result.user_id
        }
        code = 200
    else:
        json_result = {"error": "Element does not exist"}
        code = 404
    return make_response(jsonify(json_result), code)
