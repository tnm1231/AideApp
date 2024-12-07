from flask import render_template, request, jsonify
import subprocess
from flask.views import MethodView
from flask import Blueprint
import os
from .tasks import run_scan_task
from celery.result import AsyncResult
from .tasks import celery
from datetime import datetime
from app.models.models import db, TaskRecord
from celery import Celery
from uuid import uuid4


routes_blueprint = Blueprint("routes", __name__)

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
            command.extend(["--verbose=5"])
        elif check_type == "customConfig" and custom_config:
            command.extend(["--config", custom_config])
        elif check_type == "customConfigAndFile" and custom_config and specific_file:
            command.extend(["--config", custom_config, "--limit", specific_file])
        task_id = str(uuid4()) 
        task_record = TaskRecord (
            task_id = task_id,
            name=task_name,
            check_type=check_type,
            specific_file=specific_file,
            custom_config=custom_config,
            status="Started",
            progress=1
        )

        db.session.add(task_record)
        db.session.commit()
        task = run_scan_task.delay(command)
        update = self.updateStatus(task_id)
        print(task.get())
        return task.get()
    
    def updateStatus(self, task_id):
        # task = TaskRecord.query.get(task_id)
        task = TaskRecord.query.filter_by(task_id=task_id).first()
        try: 
            if task:
                task.status = "Completed"
                db.session.commit()
                return {'success': True, 'message': 'Task completed'}
            else:
                return {'success': False, 'message': 'Task not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
    def checkType(self, check_type):
        valid_check_types = [
            "customConfigAndFile", "customConfig", 
            "detailCheck", "specificFile", "fullSystem"
        ]
        if check_type not in valid_check_types:
            return jsonify({'error': f"Check type '{check_type}' is not valid."}), 400
        return None


# class này chưa chạy đc 
class ResultAnalysis(MethodView):
    def saveResult(self, result):
        return None


class TaskStatusView(MethodView):
    def get(self, task_id):
        task = AsyncResult(task_id, app=celery)

        if task.state == 'PENDING':
            response = {"status": "Pending", "progress": 0}
        elif task.state == 'SUCCESS':
            response = {"status": "Completed", "result": task.result}
        elif task.state == 'FAILURE':
            response = {"status": "Failed", "error": str(task.result)}
        else:
            response = {"status": task.state}

        return jsonify(response)        
    

