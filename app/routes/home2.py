from flask import render_template
from flask.views import MethodView


def getViewHome():
    return render_template("admin/page/home2.html")
