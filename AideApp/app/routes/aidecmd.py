import subprocess, logging
from flask import jsonify


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command):
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=35000
        )
        logging.debug(f"Command output: {result.stdout}")
        logging.debug(f"Command error: {result.stderr}")

        if result.returncode != 0:
            logging.error(f"Command failed with error: {result.stderr.strip()}")
            return {"error": result.stderr.strip()}
        else:
            print(f"Command succeeded: {result.stdout.strip()}")
            logging.info(f"Command succeeded: {result.stdout.strip()}")
            return {"output": result.stdout.strip()}
        # print("ket qua chay compare", result.stderr.strip())
        # return {"output": result.stdout.strip()}
    except subprocess.TimeoutExpired:
        logging.error("Command timed out.")
        return {"error": "Command timed out. Please try again."}
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"error": str(e)}

def compare():
    command = ["aide", "--config=/etc/aide/aide.conf", "--compare"]
    print("Vo duoc compare")
    result = run_command(command)
    if "error" in result:
        print("compare error: ", result.get("error"))
    else:
        print("compare output: ", result.get("output"))
    return jsonify(result)