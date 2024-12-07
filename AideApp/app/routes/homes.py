from flask import render_template
from flask.views import MethodView
from flask import Blueprint

routes_blueprint = Blueprint("routes", __name__)

class HomeView(MethodView):
    def get(self):
        return render_template("admin/share/master.html")
