from flask import Blueprint, render_template
from .checks import CheckView, TaskStatusView
from .homes import HomeView
routes_blueprint = Blueprint('routes', __name__)

routes_blueprint.add_url_rule('/', view_func=HomeView.as_view('home'))
# routes_blueprint.add_url_rule('/check', view_func=CheckView.as_view('checks'))
check_view =CheckView.as_view('check')
routes_blueprint.add_url_rule('/check', view_func=check_view, methods=['GET', 'POST'])


# routes_blueprint.add_url_rule('/tasks', view_func=TaskAPI.as_view('tasks'))
# routes_blueprint.add_url_rule('/tasks/<task_id>', view_func=TaskAPI.as_view('task_status'))
# routes_blueprint.add_url_rule('tasks/<task_id>/control', view_func=TaskControlAPI.as_view('task_control'))

routes_blueprint.add_url_rule('/task_status/<task_id>', view_func=TaskStatusView.as_view('task_status'))