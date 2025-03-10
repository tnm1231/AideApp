import subprocess
from flask import render_template, request, jsonify
from app.models.models import db, CronJob  # CronJob is the model
from flask.views import MethodView

AIDE_CONFIG_PATH = '/etc/default/aide'


class CronJobView(MethodView): 
    def get(self):
        return render_template("admin/page/cronJob.html")

    def post(self):
        try:
            cronjob_name = request.form.get('name', '').strip() or None
            config_file = request.form.get('configFile', '').strip() or None
            minute = request.form.get('minute', '').strip()
            hour = request.form.get('hour', '').strip()
            day = request.form.get('day', '').strip()
            month = request.form.get('month', '').strip()
            weekday = request.form.get('week', '').strip()
            mailTo = request.form.get('mail', '').strip()
            mailSubject = request.form.get('mailSubject', '').strip()
            quiteReport = request.form.get('quiteReport', '').strip()
            self.write_config(mailTo, mailSubject, quiteReport)

            # Construct cron job command
            if not any([minute, hour, day, month, weekday]):
                cronjob_entry = f"@reboot /usr/share/aide/bin/dailyaidecheck --crondaily --config=/etc/aide/{config_file}" if config_file else "@reboot /usr/share/aide/bin/dailyaidecheck --crondaily"
            else:
                aide_command = f"/usr/share/aide/bin/dailyaidecheck --crondaily --config=/etc/aide/{config_file}" if config_file else "/usr/share/aide/bin/dailyaidecheck --crondaily"
                cronjob_entry = f"{minute} {hour} {day} {month} {weekday} {aide_command}"

            # Save to database
            new_cronjob = CronJob(
                name=cronjob_name,
                config_file=config_file,
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                weekday=weekday
            )
            db.session.add(new_cronjob)
            db.session.commit()

            print(f"Crontab entry: {cronjob_entry}")
            print(f"Cron job name: {cronjob_name}")
            print(f"Config file: {config_file}")

            # Add cron job to system
            process = subprocess.run(
                f'(crontab -l; echo "{cronjob_entry}") | crontab -',
                shell=True,
                text=True,
                capture_output=True
            )

            if process.returncode != 0:
                return jsonify({"error": f"Failed to add cronjob: {process.stderr}"}), 500

            return jsonify({"message": f"Cron job '{cronjob_name}' created successfully!"}), 200

        except Exception as e:
            return jsonify({"error": f"Exception occurred: {str(e)}"}), 500


    def delete(self, cronId):
        try:
            task = CronJob.query.filter_by(id=cronId).first()
            if task:
                db.session.delete(task)
                db.session.commit()
                return jsonify({"success": True}), 200
            else:
                return jsonify({"error": "Cron job not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    # def write_config(self, mail, subject):
    #     config = {
    #         'MAILSUBJ': subject,
    #         'MAILTO': mail
    #     }
    #     with open(AIDE_CONFIG_PATH, 'w') as file:
    #         for key, value in config.items():
    #             file.write(f'{key}="{value}"\n')
    def write_config(self, mail, subject, quiteReport):
        config_lines = []
        updated_keys = {"MAILSUBJ": subject, "MAILTO": mail, "QUIETREPORTS": quiteReport}
        
        try:
            # Đọc nội dung file hiện tại
            with open(AIDE_CONFIG_PATH, 'r') as file:
                config_lines = file.readlines()

            # Cập nhật giá trị hoặc thêm mới nếu chưa tồn tại
            updated = {key: False for key in updated_keys}

            for i, line in enumerate(config_lines):
                key, sep, value = line.partition("=")
                key = key.strip()
                if key in updated_keys:
                    config_lines[i] = f'{key}="{updated_keys[key]}"\n'
                    updated[key] = True
            
            # Thêm các dòng mới nếu chưa có
            for key, value in updated_keys.items():
                if not updated[key]:
                    config_lines.append(f'{key}="{value}"\n')

            # Ghi lại file với các giá trị đã cập nhật
            with open(AIDE_CONFIG_PATH, 'w') as file:
                file.writelines(config_lines)

        except Exception as e:
            print(f"Error updating config: {e}")


    # def post(self):
    #     task_name = request.form.get('taskName')
    #     check_type = request.form.get('checkType')
    #     specific_file = request.form.get('specificFile')
    #     custom_config = request.form.get('customConfig')
# def run_aide_cronjob():
#     try:
#         startup = request.form.get('startup', 'no')
#         cronjob_name = request.form.get('name')
#         print(f"Cron job name: {cronjob_name}")

#         # config_file = request.form.get('configFile')
#         # print(f"Config file: {config_file}")
#         config_file = request.form.get('configFile', '').strip()  # Lấy giá trị và loại bỏ khoảng trắng


#         if startup == 'yes':
#             cronjob_entry = f"@reboot /usr/share/aide/bin/dailyaidecheck --crondaily --config={config_file}" if config_file else "@reboot /usr/share/aide/bin/dailyaidecheck --crondaily"
#         else:
#             minute = request.form.get('minute') or '*'
#             hour = request.form.get('hour') or '*'
#             day = request.form.get('day') or '*'
#             month = request.form.get('month') or '*'
#             weekday = request.form.get('week') or '*'

#             print(f"Minute: {minute}, Hour: {hour}, Day: {day}, Month: {month}, Weekday: {weekday}")

#             aide_command = f"/usr/share/aide/bin/dailyaidecheck --crondaily --config={config_file}" if config_file else "/usr/share/aide/bin/dailyaidecheck --crondaily"
#             cronjob_entry = f"{minute} {hour} {day} {month} {weekday} {aide_command}"

#         new_cronjob = CronJob(
#             name=cronjob_name,
#             config_file=config_file,
#             minute=minute,
#             hour=hour,
#             day=day,
#             month=month,
#             weekday=weekday,
#             startup=startup
#         )
#         db.session.add(new_cronjob)
#         db.session.commit()

#         print(f"Crontab entry: {cronjob_entry}")

#         # Thêm vào crontab
#         process = subprocess.run(
#             f'(crontab -l; echo "{cronjob_entry}") | crontab -',
#             shell=True,
#             text=True,
#             capture_output=True
#         )

#         # Kiểm tra lỗi khi chạy subprocess
#         if process.returncode != 0:
#             return jsonify({"error": f"Failed to add cronjob: {process.stderr}"}), 500

#         return jsonify({"message": f"Cron job '{cronjob_name}' created successfully!"}), 200

#     except Exception as e:
#         return jsonify({"error": f"Exception occurred: {str(e)}"}), 500

