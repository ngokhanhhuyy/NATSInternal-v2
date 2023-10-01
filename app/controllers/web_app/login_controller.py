from sqlalchemy import *
from flask import *
from flask import session as clientSession
from app import application
from app.services.authentication_service import AuthenticationService, loginRequired
from app.forms import LoginFormModel
from app.errors import AuthenticationError
from app.config import Config
from typing import List

@application.route("/login", methods=["GET", "POST"])
def login():
    # If user has already logged in, redirect to home instead
    userID = clientSession.get("userID")
    sessionToken = clientSession.get("sessionToken")
    if userID is not None and sessionToken is not None:
        return redirect(url_for("home"))
    
    # Perform login operation
    messages: List[str] = []
    form = LoginFormModel(request.form)
    if request.method == "GET":
        return render_template(
            "login.html",
            title=Config.APP_NAME,
            form=form,
            messages=None)
    else:
        if form.validate():
            try:
                loginResult = AuthenticationService.login(
                    userName=form.userName.data,
                    password=form.password.data)
                clientSession["userID"] = loginResult["userID"]
                clientSession["sessionToken"] = loginResult["sessionToken"]
                # Redirect user back to previous URL
                beforeLoginURL = clientSession.get("beforeLoginURL")
                if beforeLoginURL is not None and beforeLoginURL:
                    return redirect(clientSession.get("beforeLoginURL"))
                else:
                    return redirect(url_for("home"))
            except AuthenticationError as exception:
                messages.append(exception.text)
        else:
            messages += list(form.userName.errors) + list(form.password.errors)
        return render_template(
            "login.html",
            title=Config.APP_NAME,
            form=form,
            messages=messages)

@application.route("/logout", methods=["GET"])
@loginRequired
def logout():
    AuthenticationService.logout()
    clientSession.pop("userID")
    clientSession.pop("sessionToken")
    return redirect(url_for("login"))