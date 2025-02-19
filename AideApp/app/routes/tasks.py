from celery import Celery
import subprocess
import logging
from celery.result import AsyncResult
# from app.routes.taskHandle import TaskStatusView  
from flask import jsonify
from celery.signals import task_prerun, task_postrun, task_failure, task_success
from app.models.models import db, TaskRecord
from app.routes.taskHandle import TaskStatusView
import redis
import time

celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

class ObservableDict(dict):
    def __setitem__(self, key, value):
        # Gọi phương thức gốc để thêm key-value vào dict
        super().__setitem__(key, value)
        # In ra thông báo khi có thay đổi
        print(f"New entry added to task_pid_map: {key} -> {value}")
        print(f"Updated task_pid_map: {self}")
        
task_pid_map = ObservableDict()

@celery.task(bind=True)
def long_running_task(self, task_id):
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    current_iteration = 0
    total_iterations = 100

    # Kiểm tra Redis key và logging
    logger.info(f"Task {task_id} started")
    saved_iteration = redis_client.get(f"task:{task_id}:iteration")
    if saved_iteration:
        current_iteration = int(saved_iteration)

    while current_iteration < total_iterations:
        # Kiểm tra trạng thái Redis
        status = redis_client.get(f"task:{task_id}:status")
        logger.info(f"Task {task_id} Redis status: {status}")

        if status and status.decode('utf-8') == "paused":
            print("co vao duoc day khong")
            self.update_state(state="PAUSED", meta={'iteration': current_iteration})
            redis_client.set(f"task:{task_id}:iteration", current_iteration)
            logger.info(f"Task {task_id} paused at iteration {current_iteration}")

            while status and status.decode('utf-8') == "paused":
                time.sleep(1)  # Chờ resume
                status = redis_client.get(f"task:{task_id}:status")

        # Thực hiện công việc
        logger.info(f"Task {task_id} running iteration {current_iteration}")
        time.sleep(1)

        # Cập nhật vòng lặp và trạng thái
        current_iteration += 1
        self.update_state(state="PROGRESS", meta={'iteration': current_iteration})
        redis_client.set(f"task:{task_id}:iteration", current_iteration)

    logger.info(f"Task {task_id} completed!")
    redis_client.delete(f"task:{task_id}:status")
    redis_client.delete(f"task:{task_id}:iteration")
    return f"Task {task_id} completed!"

# @task_prerun.connect
# def update_task_status_prerun(task_id, **kwargs):
#     task = TaskRecord.query.filter_by(task_id=task_id).first()
#     if task:
#         task.status = "STARTED"
#         task.progress = 10
#         db.session.commit()


# @task_success.connect
# def update_task_status_success(result, task_id, **kwargs):
#     print(f"Task hihi {task_id} succeeded hihí.")
#     task = TaskRecord.query.filter_by(task_id=task_id).first()
#     print("task task")
#     view = TaskStatusView
#     if task:
#         task.status = "SUCCESS"
#         task.proress = 100
#         db.session.commit()
#         print("save được run scan task")
#         view.save_result(task_id, result)

# @task_failure.connect
# def update_task_status_failure(task_id, exception, **kwargs):
#     task = TaskRecord.query.filter_by(task_id=task_id).first()
#     if task:
#         task.status = "FAILURE"
#         task.progress = 100
#         # save_result(task.id, str(exception))
#         db.session.commit()


def task_status(task_id):
    task = AsyncResult(task_id, app=celery) 
    if task.ready():
        return jsonify({"status": task.status, "result": task.result})
    else:
        return jsonify({"status": task.status, "result": None})
    
@celery.task(bind=True)
def run_scan_task(self, command):
    print("------------------------------------------------")
    task_id = self.request.id
    print("task id", task_id)
    # task_result = AsyncResult(task_id)
    # view = TaskStatusView
    if not isinstance(command, list) or not all(isinstance(arg, str) for arg in command):
        return {"error": "Invalid command format"}
    try:
        result = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )   
        pid = result.pid
        task_pid_map[task_id] = pid
        # print("task_pid_map: ",task_pid_map)
        # print("process id trong run scan task", pid)
        # updatePid.delay(task_id, pid)
        # updatePid.apply_async(args=[task_id, pid])


        stdout, stderr = result.communicate(timeout=20000)
        logging.debug(f"Command output: {stdout}")
        
        logging.debug(f"Command error: {stderr}")
       
        print("task result khong co strip bo khoang trang : ",result.stdout)

        return {
            "output": stdout.strip(),
            "error": stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        logging.error("Command timed out.")
        return {"error": "Command timed out. Please try again with a smaller scope."}
    except FileNotFoundError as e:
        logging.error(f"Command not found: {e}")
        return {"error": f"Command not found: {e}"}
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"error": str(e)}  


def wait_for_pid(task_id, timeout=10000, interval=10):
    print("vào được get task id")
    # print("task pid map",task_pid_map)
    # pid = task_pid_map.get(task_id)
    start_time = time.time()
    while time.time() - start_time < timeout:
        pid = task_pid_map.get(task_id)
        if pid:
            print("pid trnog get map task",pid)
            return int(pid) 
        time.sleep(interval)
    return None
    # if pid:
    #     print("Process ID in get_task_pid:", pid)
    #     return pid
    # else:
    #     return "Task ID not found or task hasn't started yet."

# def updatePid(self, task_id, pid):
        # print("vào được update pid")
        # task_record = TaskRecord.query.filter_by(task_id=task_id).first()
        # if task_record:
        #     task_record.pid = pid
        #     db.session.commit()   


