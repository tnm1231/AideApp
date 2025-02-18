from flask import render_template, request, jsonify
from flask.views import MethodView
from .tasks import run_scan_task
from app.models.models import db, TaskRecord, ResultScan
from app.routes.taskHandle import TaskStatusView
from .tasks import wait_for_pid, task_pid_map
import time

# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
class CheckView(MethodView):
    def get(self):
        task = TaskRecord.query.all()
        return render_template("admin/page/checker.html", tasks=task )

    def post(self):
        task_name = request.form.get('taskName')
        check_type = request.form.get('checkType')
        specific_file = request.form.get('specificFile')
        custom_config = request.form.get('customConfig')

        # validate_error = self.validate_paths(specific_file)
        # if validate_error:
        #     return validate_error

        # validate_error = self.validate_paths(custom_config)
        # if validate_error:
        #     return validate_error

        validate_error = self.checkType(check_type)
        if validate_error:
            return validate_error

        command = ["aide", "--check"]
        default_config = "/etc/aide/aide.conf"

        if check_type == "fullSystem":
            command.extend(["--config", default_config])
        elif check_type == "specificFile" and specific_file:
            command.extend(["--config", default_config])
            command.extend(["--limit", specific_file])
        elif check_type == "detailCheck":
            command.extend(["--config", default_config])
            command.extend(["--log-level=warning"])
        elif check_type == "customConfig" and custom_config:
            command.extend(["--config", custom_config])
        elif check_type == "customConfigAndFile" and custom_config and specific_file:
            command.extend(["--config", custom_config, "--limit", specific_file])

        task = run_scan_task.delay(command)
        task_record = TaskRecord (
            task_id = task.id,
            name=task_name,
            check_type=check_type,
            specific_file=specific_file,
            custom_config=custom_config,
            status=task.state,
            progress=0
        )
        db.session.add(task_record)
        db.session.commit()
        print("task id in check: ", task.id)
        # time.sleep(5)
        # pid = wait_for_pid(task.id, timeout=10)
        # print("Retrieved PID: ", pid)
        
        result = task.get()
        view = TaskStatusView
        view.save_result(task.id, result)
       
        self.updateState(task.id, task.state)

        return jsonify({"task_id": task.id, "status": "Task created"}), 202

    def updateState(self, task_id, state ):
        print("vào được update")
        task_record = TaskRecord.query.filter_by(task_id=task_id).first()
        
        if task_record:
            task_record.status = state
            db.session.commit()

    def checkType(self, check_type):
        valid_check_types = [
            "customConfigAndFile", "customConfig",
            "detailCheck", "specificFile", "fullSystem"
        ]
        if check_type not in valid_check_types:
            return jsonify({'error': f"Check type '{check_type}' is not valid."}), 400
        return None
