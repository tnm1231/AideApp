from flask import Blueprint, render_template
from .checks import CheckView
from .homes import HomeView
from .home2 import getViewHome
from .taskHandle import TaskStatusView, task_pause, task_resume
from .tasks import task_status
from .aidecmd import compare
from .aideConfig import CustomConfigView
from .aideConfig import check_config

routes_blueprint = Blueprint('routes', __name__)

#trang master để check 
routes_blueprint.add_url_rule('/', view_func=HomeView.as_view('home'))

#view check page method GET, check method POST create task (post form)
check_view =CheckView.as_view('check')
routes_blueprint.add_url_rule('/check', view_func=check_view, methods=['GET', 'POST'])

#status này chưa làm được
# routes_blueprint.add_url_rule('/task-status/<task_id>', view_func=TaskStatusView.as_view('task_status'))

#delete task
task_view = TaskStatusView.as_view('delete')
routes_blueprint.add_url_rule('/delete-task/<string:task_id>', view_func=task_view, methods=['DELETE'])

#suspend/resume task
routes_blueprint.add_url_rule('/task-pause/<string:task_id>', 'task_pause', task_pause, methods=['POST'])
routes_blueprint.add_url_rule('/task-resume/<string:task_id>','task_resume', task_resume, methods=['POST'])

# view result taskcd 
routes_blueprint.add_url_rule('/get-result/<string:task_id>', view_func=TaskStatusView.as_view('getTask'), methods=['GET'])
#task status 
routes_blueprint.add_url_rule('/task-status/<string:task_id>', view_func=task_status, methods=['GET'])

config_view = CustomConfigView.as_view('config')
routes_blueprint.add_url_rule('/config', view_func=config_view, methods=['GET', 'POST'])
routes_blueprint.add_url_rule('/check-config', view_func=check_config, methods=['POST'])


routes_blueprint.add_url_rule('/compare-aide-database', 'compare', compare, methods=['POST'])

# routes_blueprint.add_url_rule('/tasks', view_func=TaskAPI.as_view('tasks')
# routes_blueprint.add_url_rule('/tasks/<task_id>', view_func=TaskAPI.as_view('task_status'))
# routes_blueprint.add_url_rule('tasks/<task_id>/control', view_func=TaskControlAPI.as_view('task_control'))
# routes_blueprint.add_url_rule('/check', view_func=CheckView.as_view('checks'))




#route mail
