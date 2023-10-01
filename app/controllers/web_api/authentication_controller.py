from app import application
from app.extensions.date_time import *
from flask import *
from app.schemas.authentication_schema import AuthenticationSchema
from app.services.authentication_service import AuthenticationService, AuthenticationError
from typing import Dict
from pydantic import ValidationError

@application.route("/api/apiKey", methods=["POST"])
def getAPIKey():
    try:
        requestedData = request.get_json()
        if requestedData is None:
            return {
                "error": "ValueError",
                "descrption": "Request format or value is invalid"
            }, 400
        requestedStaff = AuthenticationSchema(**requestedData)
        requestedIPAddress = request.remote_addr
        requestedUserAgent = request.headers.get("User-Agent", type=str)
        authenticationData: Dict[str, str] = AuthenticationService.getAPIToken(
            staffUserName=requestedStaff.userName,
            staffPassword=requestedStaff.password,
            staffIPAddress=requestedIPAddress,
            staffUserAgent=requestedUserAgent)
        return jsonify(authenticationData)
    except ValidationError as exception:
        return {
            "error":        type(exception).__name__,
            "description":  "Username and password is invalid"
        }, 400
    except AuthenticationError as exception:
        return {
            "error": type(exception).__name__,
            "description": str(exception)
        }, 401