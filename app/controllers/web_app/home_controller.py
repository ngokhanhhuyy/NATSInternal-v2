from flask import *
from app import application
from app.services.authentication_service import loginRequired
from app.extensions.date_time import Time
from app.data import getDatabaseSession

@application.route("/", endpoint="home", methods=["GET"])
@application.route("/home", endpoint="home", methods=["GET"])
@application.route("/home/", endpoint="home", methods=["GET"])
@loginRequired
def home():
    return render_template("home.html")

