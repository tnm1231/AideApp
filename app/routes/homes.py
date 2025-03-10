from flask import render_template
from flask.views import MethodView


class HomeView(MethodView):
    def get(self):
        return render_template("admin/page/home.html")
