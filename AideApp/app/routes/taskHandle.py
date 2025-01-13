from flask.views import MethodView
from celery.result import AsyncResult
from celery import Celery
from flask import request, jsonify
from app.models.models import db, TaskRecord, ResultScan
import redis
import re 
import logging
import time


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def get_task_state(task_id):
    result = AsyncResult(task_id)
    return result.state

def task_pause(task_id):  
    print("Vô được task paused")
    try:
        redis_client.set(f"task:{task_id}:status", "paused")
        updateState(task_id, "PAUSED")

        # celery_state = get_task_state(task_id)
        # print("celery state: ", celery_state)

        return jsonify({'success': True, 'message': f'Task {task_id} paused.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def task_resume(task_id):  
    print("Vô được task resume")
    try:
        redis_client.set(f"task:{task_id}:status", "running")
        updateState(task_id, "RESUMED")

        # celery_state = get_task_state(task_id)
        # print("celery state: ", celery_state)

        return jsonify({'success': True, 'message': f'Task {task_id} resumed.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def updateState(task_id, state ):
        task_record = TaskRecord.query.filter_by(task_id=task_id).first()
        
        if task_record:
            task_record.status = state
            db.session.commit()    

def updatePid(task_id, pid ):
        print("vào được update pid")
        task_record = TaskRecord.query.filter_by(task_id=task_id).first()
        
        if task_record:
            task_record.pid = pid
            db.session.commit()    


class TaskStatusView(MethodView):
    def get(self, task_id):
        # result = db.session.query(ResultScan).filter_by(task_id=task_id).first()
        result = db.session.query(ResultScan).join(TaskRecord).filter(ResultScan.task_id == task_id).first()
        if result:
            parsed_algorithm = self.parse_algorithm_data(result.algorithm)
            
            task_record = result.task_record
            task_name = task_record.name
            task_check_type = task_record.check_type
            task_specific_file = task_record.specific_file

            return jsonify({
                "success": True,
                "data": {
                    "task_id": result.task_id,
                    "task_name": task_name,
                    "task_check_type": task_check_type,
                    "task_specific_file": task_specific_file or "",
                    "total_entries": result.total_entries or 0,
                    "added_entries": result.added_entries or 0, 
                    "removed_entries": result.removed_entries or 0,
                    "changed_entries": result.changed_entries or 0, 
                    "added_files" : result.added_files.split('\n') if result.added_files else [],
                    # detail added file sẽ thay cái này bằng 1 tên khác
                    "added_directories": result.added_directories or [],
                    "removed_files": result.removed_files or [],
                    "changed_files": result.changed_files or [],
                    "algorithm": parsed_algorithm,
                    "timestamp" : result.timestamp or "N/A"
                }
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "No result found for this task_id."
            }), 404

    
    def parse_algorithm_data(self, algorithmData):
        if not algorithmData:
            return[]
        lines = algorithmData.splitlines()
        parsed_data= []
        current_algo = None
        for line in lines:
            if ": " in line:
                algo, value = line.split(": ", 1)
                current_algo = algo.strip()
                parsed_data.append({"algorithm": current_algo, "value": value.strip()})
            elif current_algo:
                parsed_data[-1]["value"] += " " + line.strip()

        return parsed_data
        
    def delete(self, task_id):
        try:
            task = TaskRecord.query.filter_by(task_id=task_id).first()
            if task:
                ResultScan.query.filter_by(task_id=task_id).delete()
                db.session.delete(task)
                db.session.commit()
                return jsonify({"success": True}), 200
            else:
                return jsonify({"error": "Task not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    def save_result(task_id, scan_result):
        print("task id in save result", task_id)
        try:
            if task_id is None or not scan_result or 'output' not in scan_result:
                raise ValueError("Task ID or scan result is not valid!")

            output = scan_result['output']

            total_entries = re.search(r"Total number of entries:\s+(\d+)", output)
            added_entries = re.search(r"Added entries:\s+(\d+)", output)
            removed_entries = re.search(r"Removed entries:\s+(\d+)", output)
            changed_entries = re.search(r"Changed entries:\s+(\d+)", output)

            print ("total_entries: ",total_entries, ",added_entries: ",added_entries, ",removed_entries: ", removed_entries,",changed_entries:", changed_entries)

            result = ResultScan(
                task_id=task_id,
                total_entries=int(total_entries.group(1)) if total_entries else None,
                added_entries=int(added_entries.group(1)) if added_entries else None,
                removed_entries=int(removed_entries.group(1)) if removed_entries else None,
                changed_entries=int(changed_entries.group(1)) if changed_entries else None
            )
            # added_files = re.findall(r"^f\+.+", output, re.MULTILINE)
            # added_dirs = re.findall(r"^d\+.+", output, re.MULTILINE)
            added_file_dir = re.findall(r"^[fd]\+.+", output, re.MULTILINE)

            removed_files= re.findall(r"^f\-.+", output, re.MULTILINE)
            changed_files = re.findall(r"^f\~.+", output, re.MULTILINE)

            algorithm_data = re.search(r"The attributes of the \(uncompressed\) database\(s\):\n-+\n(.*?)(?=\nEnd timestamp:|\Z)", output, re.DOTALL)
            end_timestamp = re.search(r"End timestamp:.*", output)
           
            result.timestamp = end_timestamp.group(0) if end_timestamp else None
            result.algorithm = algorithm_data.group(1).strip() if algorithm_data else None
            result.added_files = "\n".join(added_file_dir) if added_file_dir else None
            result.removed_files = "\n".join(removed_files) if removed_files else None
            result.changed_files = "\n".join(changed_files) if changed_files else None

            db.session.add(result)
            db.session.commit()

        except Exception as e:
            print(f"Error in save result to database!: {e}")   