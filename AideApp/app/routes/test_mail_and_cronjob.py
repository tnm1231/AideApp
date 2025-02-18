import os
from flask import render_template, request, redirect, url_for, flash
from flask.views import MethodView

# Đường dẫn tới file AIDE config
AIDE_CONFIG_PATH = '/var/www/html/AideApp/AideApp/aide'

class TestMailView(MethodView):
    def get(self):
        config = self.read_config()
        # Trả về template (HTML) kèm theo config
        return render_template('admin/page/mail2.html', config=config)

    def post(self):
        # Thu thập dữ liệu từ form (name field trong HTML)
        config = {
            'CRON_DAILY_RUN':         request.form.get('cron_daily_run', 'no'),
            'FQDN':                   request.form.get('fqdn', ''),
            'MAILSUBJ':               request.form.get('mailsubj', ''),
            'MAILTO':                 request.form.get('mailto', ''),
            'MAILCMD':                request.form.get('mailcmd', ''),
            'MAILWIDTH':              request.form.get('mailwidth', '990'),
            'QUIETREPORTS':           request.form.get('quietreports', 'no'),
            'SILENTREPORTS':          request.form.get('silentreports', 'no'),
            'FIGLET':                 request.form.get('figlet', 'yes'),
            'COMMAND':                request.form.get('command', 'check'),
            'COPYNEWDB':              request.form.get('copynewdb', 'no'),
            'TRUNCATEDETAILS':        request.form.get('truncatedetails', 'no'),
            'FILTERUPDATES':          request.form.get('filterupdates', 'no'),
            'FILTERINSTALLATIONS':    request.form.get('filterinstallations', 'no'),
            'LINES':                  request.form.get('lines', '1000'),
            'NOISE':                  request.form.get('noise', ''),
            'AIDEARGS':               request.form.get('aideargs', ''),
            'CRONEXITHOOK':           request.form.get('cronexithook', '')
        }

        # Ghi config ra file
        self.write_config(config)
        flash('Configuration updated successfully!', 'success')
        return redirect(url_for('routes.mail'))  # routes.mail -> Tên endpoint tương ứng

    def read_config(self):
        """
        Đọc file config, trả về dict { key: value }
        Bỏ qua dòng comment (#) hoặc dòng không có dấu '='
        """
        config = {}
        if not os.path.exists(AIDE_CONFIG_PATH):
            return config  # File chưa tồn tại -> trả về dict rỗng

        with open(AIDE_CONFIG_PATH, 'r') as f:
            for line in f:
                line = line.strip()
                # Bỏ qua comment hoặc dòng trống
                if not line or line.startswith('#') or '=' not in line:
                    continue
                # Tách key=value
                key, value = line.split('=', 1)
                key = key.strip()
                # Loại bỏ dấu " nếu có
                value = value.strip().strip('"').strip("'")
                config[key] = value
        return config

    def write_config(self, config_dict):
        """
        Ghi toàn bộ các key/value từ config_dict xuống file, dạng key="value"
        Lưu ý: Hành vi này sẽ xóa comment / các dòng không nằm trong dict.
        """
        with open(AIDE_CONFIG_PATH, 'w') as f:
            for key, value in config_dict.items():
                f.write(f'{key}="{value}"\n')
