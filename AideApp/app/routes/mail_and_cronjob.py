import os
from flask import render_template, request, redirect, url_for, flash
from flask.views import MethodView

AIDE_CONFIG_PATH = '/var/www/html/AideApp/AideApp/aide'

class MailView(MethodView):
    def get(self):
        config = self.read_config()
        return render_template('admin/page/mail.html', config=config)

    def post(self):
        config = {
            'CONFIG': request.form.get('CONFIG'),
            'FQDN': request.form.get('FQDN'),
            'MAILSUBJ': request.form.get('MAILSUBJ'),
            'MAILTO': request.form.get('MAILTO'),
            'MAILCMD': request.form.get('MAILCMD'),
            'MAILWIDTH': request.form.get('MAILWIDTH'),
            'COMMAND': request.form.get('COMMAND'),
            'COPYNEWDB': request.form.get('COPYNEWDB'),
            'AIDEARGS': request.form.get('AIDEARGS')
        }
        self.write_config(config)
        flash('Configuration updated successfully!', 'success')
        return redirect(url_for('routes.mail'))

    def read_config(self):
        config = {}
        with open(AIDE_CONFIG_PATH, 'r') as file:
            for line in file:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value.strip('"')
        return config

    def write_config(self, config):
        with open(AIDE_CONFIG_PATH, 'w') as file:
            for key, value in config.items():
                file.write(f'{key}="{value}"\n')
