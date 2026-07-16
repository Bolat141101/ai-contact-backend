from flask import Blueprint, render_template

blueprint = Blueprint("web", __name__)


@blueprint.get("/")
def index():
    return render_template("index.html")


@blueprint.get("/monitoring")
def monitoring():
    return render_template("monitoring.html")
