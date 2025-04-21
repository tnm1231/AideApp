import os
from flask import render_template, request, redirect, url_for, flash
from flask.views import MethodView

# Đường dẫn tới file cấu hình AIDE
# AIDE_CONFIG_PATH = '/var/www/html/AideApp/AideApp/aide'
AIDE_CONFIG_PATH = '/etc/default/aide'

class MailView(MethodView):
    def get(self):
        # Đọc file config -> trả về template kèm dict config
        config = self.read_config()
        return render_template('admin/page/mail.html', config=config)

    def post(self):
        # Lấy giá trị từ form. Nếu key không tồn tại trong form, lấy giá trị mặc định.
        config = {
            'CONFIG':              request.form.get('CONFIG', '/etc/aide/aide.conf'),
            'CRON_DAILY_RUN':      request.form.get('CRON_DAILY_RUN', 'no'),
            'FQDN':                request.form.get('FQDN', ''),
            'MAILSUBJ':            request.form.get('MAILSUBJ', ''),
            'MAILTO':              request.form.get('MAILTO', ''),
            'MAILCMD':             request.form.get('MAILCMD', ''),
            'MAILWIDTH':           request.form.get('MAILWIDTH', '990'),
            'QUIETREPORTS':        request.form.get('QUIETREPORTS', 'no'),
            'SILENTREPORTS':       request.form.get('SILENTREPORTS', 'no'),
            'FIGLET':              request.form.get('FIGLET', 'yes'),
            'COMMAND':             request.form.get('COMMAND', 'check'),
            'COPYNEWDB':           request.form.get('COPYNEWDB', 'no'),
            'TRUNCATEDETAILS':     request.form.get('TRUNCATEDETAILS', 'no'),
            'FILTERUPDATES':       request.form.get('FILTERUPDATES', 'no'),
            'FILTERINSTALLATIONS': request.form.get('FILTERINSTALLATIONS', 'no'),
            'LINES':               request.form.get('LINES', '1000'),
            'NOISE':               request.form.get('NOISE', ''),
            'AIDEARGS':            request.form.get('AIDEARGS', ''),
            'CRONEXITHOOK':        request.form.get('CRONEXITHOOK', '')
        }
        # Ghi config ra file
        self.write_config(config)

        flash('Configuration updated successfully!', 'success')
        return redirect(url_for('routes.mail'))  # Giả sử endpoint này tên 'routes.mail'

    def read_config(self):
        """
        Đọc file config, trả về dict {key: value} cho các dòng dạng key="value"
        Bỏ qua comment (#) hoặc dòng trống. 
        """
        config = {}
        if not os.path.exists(AIDE_CONFIG_PATH):
            return config  # File chưa tồn tại -> trả về dict rỗng

        with open(AIDE_CONFIG_PATH, 'r') as file:
            for line in file:
                line = line.strip()
                # Bỏ qua comment hoặc dòng trống
                if not line or line.startswith('#'):
                    continue
                # Kiểm tra xem có ký tự '='
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"')  # Bỏ dấu " nếu có
                    config[key] = value
        return config

    def write_config(self, config):
        """
        Ghi toàn bộ key/value xuống file theo định dạng key="value". 
        Các dòng cũ sẽ bị ghi đè (bao gồm comment).
        """
        with open(AIDE_CONFIG_PATH, 'w') as file:
            for key, value in config.items():
                file.write(f'{key}="{value}"\n')
