import subprocess, logging
from flask import jsonify
import threading
from flask import Flask, request, jsonify
import os
import json


# from flask_cors import CORS  

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
    output_file = "/home/Phu/AideApp/instance/aide-compare-result.txt"
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout.strip()
        error = result.stderr.strip()
        print("output compare", result.stdout.strip())
        
        with open(output_file, "w") as f:
            f.write(output)
            f.write(error)

        return {"output": output, "error": error, "returncode": result.returncode}
    except Exception as e:
        return {"error": str(e)}
    
COMPARE_FILE = "/home/Phu/AideApp/instance/aide-compare-result.txt"

def compareResult():
    if not os.path.exists(COMPARE_FILE):  # Kiểm tra file tồn tại
        return jsonify({"errors": "File not found"}), 404
    try:
        with open(COMPARE_FILE, "r", encoding="utf-8") as f:
            content = json.load(f)
            # content = content.json()
            print(content["start_time"])  
                  
            # print("content", content)
            return jsonify({"filename": COMPARE_FILE, "content": content})
    except Exception as e:
        return jsonify({"errors": str(e)}), 500






def run_aide(firstChoice, secondChoice):
    """Chạy aideinit và phản hồi theo từng câu hỏi"""
    try:
        # Xây dựng dữ liệu nhập vào stdin
        input_data = firstChoice + "\n"
        if firstChoice.lower() == "yes":
            input_data += secondChoice + "\n"

        # Mở tiến trình aideinit với PIPE để gửi input vào stdin
        process = subprocess.Popen(
            ["aideinit"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Gửi toàn bộ input vào stdin và lấy output/error
        output, error = process.communicate(input=input_data)

        # Xác định kết quả chạy
        if process.returncode == 0:
            return {"status": "success", "output": output.strip() or "AIDE update completed successfully."}
        else:
            return {"status": "error", "message": error.strip() or "Unknown error occurred."}

    except BrokenPipeError:
        return {"status": "error", "message": "Broken Pipe Error: aideinit có thể đã đóng stdin sớm hơn dự kiến."}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

def update():
    data = request.get_json()
    firstChoice = data.get("firstChoice", "").lower()

    secondChoice = data.get("secondChoice")
    if secondChoice is None:
        secondChoice = ""
    else:
        secondChoice = secondChoice.lower()

    if firstChoice not in ["yes", "no"] or secondChoice not in ["yes", "no", ""]:
        return jsonify({"status": "error", "message": "Invalid choices"}), 400

    secondChoice = secondChoice if firstChoice == "yes" else ""

    result = run_aide(firstChoice, secondChoice)

    if result["status"] == "error":
        print("Command error:", result["message"])
    else:
        print("Command output:", result["output"])

    return jsonify(result)
   
