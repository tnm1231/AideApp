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
            timeout=20000
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
    print("compare")
    command = ["aide", "--compare", "--config=/etc/aide/aide.conf"]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("output compare", result.stdout.strip())
        return {"output": result.stdout.strip(), "error": result.stderr.strip(), "returncode": result.returncode}
    except Exception as e:
        return {"error": str(e)}

def update():
    print("update")
    command = ["aide", "--updates", "--config=/etc/aide/aide.conf"]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("output compare", result.stdout.strip())
        return {"output": result.stdout.strip(), "error": result.stderr.strip(), "returncode": result.returncode}
    except Exception as e:
        return {"error": str(e)}

# def compare():
#     command = ["aide", "--config=/etc/aide/aide.conf", "--compare"]
#     print("Vo duoc compare")
#     result = run_command(command)
#     if "error" in result:
#         print("compare error: ", result.get("error"))
#     else:
#         print("compare output: ", result.get("output"))
#     print("output compare: ", result)
#     return jsonify(result)


# def compare():
#     print("compare")
#     try:
#         result = subprocess.run(
#             ["aide", "--config=/etc/aide/aide.conf", "--compare"],
#             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=35000
#         )
#         output, error = result.stdout.strip(), result.stderr.strip()

#         if result.returncode != 0:
#             logging.error(f"Compare failed: {error}")
#             return jsonify({"error": error})
        
#         logging.info(f"Compare succeeded: {output}")
#         return jsonify({"output": output})
    
#     except subprocess.TimeoutExpired:
#         logging.error("Compare command timed out.")
#         return jsonify({"error": "Command timed out. Please try again."})
#     except Exception as e:
#         logging.error(f"Unexpected error: {e}")
#         return jsonify({"error": str(e)})
