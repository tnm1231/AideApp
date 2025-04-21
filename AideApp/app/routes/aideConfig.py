from flask import render_template, request, redirect, url_for, flash, send_file
from flask.views import MethodView
import subprocess
from flask import jsonify
import re

def run_aide_check(config_lines):
    """
    Chạy AIDE kiểm tra config và xử lý từng lỗi bằng cách comment dòng lỗi.
    """
    errors = []
    modified_config = config_lines[:]  # Sao chép danh sách dòng config
    while True:
        # Chạy kiểm tra với toàn bộ file config
        config_text = "\n".join(modified_config)
        result = subprocess.run(
            ["aide", "--config-check", "--config", "-"],
            input=config_text, capture_output=True, text=True
        )

        output = result.stderr.strip() or result.stdout.strip()

        # Nếu không có lỗi nào thì thoát vòng lặp
        if not output:
            break

        # print("🔥 AIDE OUTPUT 🔥")
        # print(output)

        # Trích xuất số dòng bị lỗi từ thông báo của AIDE
        match = re.search(r'\(stdin\):(\d+):', output)
        if not match:
            errors.append(f"Unknown error format from AIDE: {output}")
            break  # Dừng nếu không thể tìm được số dòng lỗi

        error_line = int(match.group(1))  # Lấy số dòng bị lỗi
        errors.append(f"Line {error_line}: {output}")

        # Comment dòng lỗi đó
        if 0 < error_line <= len(modified_config):
            modified_config[error_line - 1] = f"# {modified_config[error_line - 1]}  # COMMENTED BY SCRIPT"

    return errors

def check_config():
    print("Vào được check config")
    data = request.json
    config_content = data.get("config_text", "").strip()  # Lấy nội dung config

    if not config_content:
        return jsonify({"errors": ["No configuration provided"]})

    # errors = run_aide_check(config_content)
    config_lines = config_content.split("\n")
    errors = run_aide_check(config_lines)

    return jsonify({"errors": errors})


class CustomConfigView(MethodView):
    def get(self):
        return render_template("admin/page/configure.html")
    
    def post(self):
        try:
            # Retrieve form data
            config_file_name = request.form.get('config_file_name')
            print("config_file_name",config_file_name)

            if not config_file_name:
                return {"error": "Config file name is required."}, 400
            
            config_file_path = f"/etc/aide/{config_file_name}"
            
            # Gather other form data
            
            rules_mapping = {
                'normal_rule_button' : 'p+i+n+u+g+s+m+c+sha256',
                'dataonly_rule_button': 'p+u+g+s+xattrs+sha256',
            }
            rules = {key: value for key, value in rules_mapping.items() if request.form.get(key) == 'true'}
            
            normal_rule = rules.get('normal_rule_button','')
            dataonly_rule = rules.get('dataonly_rule_button', '')
            
            upac_settings = request.form.get('upac_settings', '')
            environment_path = request.form.get('environment_path', '')
            database = request.form.get('database', '')
            database_out = request.form.get('database_out', '')
            database_new = request.form.get('database_new', '')
            gzip_db_out = request.form.get('gzip_db_out', '')   # Ensure boolean value

            # Other optional fields
            report_url = request.form.get('report_url', '')
            log_level = request.form.get('log_level', '')
            report_level = request.form.get('report_level', '')
            report_base16 = request.form.get('report_base16', '') or 'false'
            print("report_base16", report_base16)
            report_summarize_changes = request.form.get('report_summarize_changes', 'no')
            report_grouped = request.form.get('report_grouped', 'no')
            database_add_metadata = request.form.get('database_add_metadata', 'no')
            custom_rules = request.form.get('custom_rules', '')
            include_directories = request.form.get('include_directories', '')
            exclude_directories = request.form.get('exclude_directories', '')
            include_list = [dir.strip() for dir in include_directories.split(',') if dir.strip()]
            exclude_list = [dir.strip() for dir in exclude_directories.split(',') if dir.strip()]

            checksum_algorithms = request.form.get('checksum_algorithms', '')
            # print("Checksume algorithms", checksum_algorithms)

            # Write to config file
            with open(config_file_path, "w") as f:
              
                f.write(f"@@x_include_setenv UPAC_settingsd {upac_settings}\n")
                f.write(f"@@x_include_setenv PATH {environment_path}\n")
                f.write(f"@@define DBDIR {database}\n")
                f.write(f"@@define LOGDIR {database_out}\n")
                f.write(f"database_in=file:{database}\n")
                f.write(f"database_out=file:{database_out}\n")
                f.write(f"database_new=file:{database_new}\n")
                if normal_rule:  # Kiểm tra nếu không rỗng
                    f.write(f"NORMAL = {normal_rule}\n")
                if dataonly_rule:  # Kiểm tra nếu không rỗng
                    f.write(f"DATAONLY = {dataonly_rule}\n")
                f.write(f"gzip_dbout={gzip_db_out}\n")
                f.write(f"report_url={report_url}\n")
                if log_level:
                    f.write(f"log_level={log_level}\n")
                if report_level:
                    f.write(f"report_level={report_level}\n")
                f.write(f"report_base16={report_base16}\n")
                f.write(f"report_summarize_changes={report_summarize_changes}\n")
                f.write(f"report_grouped={report_grouped}\n")
                f.write(f"database_add_metadata={database_add_metadata}\n")
                if custom_rules:
                    f.write("# Custom Rules\n")
                    f.write(custom_rules + "\n")
                f.write("# Directories\n")
                # f.write(include_directories + "\n")
                for directory in include_list:
                    f.write(directory + " NORMAL" "\n")
                # f.write(exclude_directories + "\n")
                for directory in exclude_list:
                    f.write("!"+ directory + "\n")
                if checksum_algorithms.strip():
                    f.write("# Checksum Algorithms\n")
                    f.write("Checksums = " + checksum_algorithms.lower() + "\n")

            return {"success": "Configuration saved successfully."}, 200
        except Exception as e:
            # Log error for debugging
            print(f"Error saving configuration: {str(e)}")
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500
