from sqlalchemy import *
from sqlalchemy.orm import *
from flask import *
from app import application
from app.services.user_service import UserService
from app.errors import DataValidationError, NotFoundError
from app.services.authentication_service import loginRequired

@application.route("/users", methods=["GET"])
@loginRequired
def userListPage():
    return "Hello"

@application.route("/user/<int:userID>", endpoint="user", methods=["GET", "POST"])
@loginRequired
def userProfilePage(userID: int):
    try:
        user = UserService.getUserByID(userID)
    except NotFoundError:
        abort(404)
    return render_template(
        "user.html",
        user=user[userID])