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
from .taskHandle import updatePid

celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)



# @celery.task(bind=True)
# def run_scan_task(self, command):
#     task_id = self.request.id
#     print("task id", task_id)
#     # task_result = AsyncResult(task_id)
#     # view = TaskStatusView
#     if not isinstance(command, list) or not all(isinstance(arg, str) for arg in command):
#         return {"error": "Invalid command format"}
#     try:
#         result = subprocess.run(
#             command,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             timeout=20000
#         )   
#         logging.debug(f"Command output: {result.stdout}")
        
#         logging.debug(f"Command error: {result.stderr}")
#         # print("task result khong co strip bo khoang trang : ",result.stdout)
#         # logging.info(f"Started process with PID: {result.pid}")
#         # print(f"Process ID (PID): {result.pid}")
#         # stdout, stderr = result.communicate(timeout=20000)
#         # returncode = result.returncode
#         # print("return code: ", returncode)
#         # print("output: ", result.stdout)
#         # print("error: ", result.stderr)
#         # if returncode != 0:
#         #     logging.error(f"Command failed with error: {stderr}")
#         #     return {"error": stderr.strip()}
        
#         # logging.debug(f"Command output: {result.stdout}")
#         return {
#             # "pid": result.pid,
#             "output": result.stdout.strip(),
#             "error": result.stderr.strip()
#         }
#         # print("task result hihi : ",result.stdout.strip())
#         # scan_result = result.stdout.strip()
#         # view.save_result(task_id, scan_result)
#         # return {
#         #     "output": result.stdout.strip(),
#         #     "error": result.stderr.strip(),
#         # }
#     except subprocess.TimeoutExpired:
#         # result.kill()
#         logging.error("Command timed out.")
#         return {"error": "Command timed out. Please try again with a smaller scope."}
#     except FileNotFoundError as e:
#         logging.error(f"Command not found: {e}")
#         return {"error": f"Command not found: {e}"}
#     except Exception as e:
#         logging.error(f"Unexpected error: {e}")
#         return {"error": str(e)}
    
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
        stdout, stderr = result.communicate(timeout=20000)
        logging.debug(f"Command output: {stdout}")
        
        logging.debug(f"Command error: {stderr}")
        pid = result.pid
        print("process id", pid)
        updatePid(task_id, pid)
        # logging.debug(f"process id: {result.pid}")
        # print("process id", result.pid)
        print("task result khong co strip bo khoang trang : ",result.stdout)

        # print("task result hihi : ",result.stdout.strip())
        # scan_result = result.stdout.strip()
        # view.save_result(task_id, scan_result)
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