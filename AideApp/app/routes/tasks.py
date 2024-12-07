from celery import Celery
import subprocess
import logging, time

celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')


@celery.task(bind=True)
def run_scan_task(self, command):
    print("da vo function run_scan_task")

    # try:
    #         result = subprocess.run(
    #             command,
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.PIPE,
    #             text=True,
    #             timeout=20000
    #         )
    #         return {
    #             "output": result.stdout,
    #             "error": result.stderr,
    #         }
    # except subprocess.TimeoutExpired:
    #     return {"error": "Command timed out. Please try again with a smaller scope."}
    # except Exception as e:
    #     return {"error": str(e)}
    
    # print("run_scantask")
    if not isinstance(command, list) or not all(isinstance(arg, str) for arg in command):
        return {"error": "Invalid command format"}
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20000  # 20 seconds timeout for testing
        )
        logging.debug(f"Command output: {result.stdout}")
        logging.debug(f"Command error: {result.stderr}")

        return {
            "output": result.stdout.strip(),
            "error": result.stderr.strip(),
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
    



   