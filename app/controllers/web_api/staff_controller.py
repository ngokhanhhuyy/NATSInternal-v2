from app import application
from flask import *
from flask import g as requestContext
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from app.data import session
from app.models.user import User
from app.services.authentication_service import authenticationRequired
from app.services.request_validation_service import JSONRequestRequired
from app.services.user_service import StaffService
from app.schemas.staff_schema import *
from app.validation import SQLModelValidationError
from pydantic import ValidationError
from typing import List, Dict, Union, Any

@application.route("/api/staffs", methods=["GET"])
@authenticationRequired
def gettingMultipleStaffs():
    try:
        # Getting staffs data by range
        if request.args.get("startingIdentity") is not None:
            rangeSchema = StaffRangeSchema(
                startingIdentity=request.args.get("startingIdentity"),
                limit=request.args.get("limit") if request.args.get("limit") != 0 else None)
            staffData = StaffService.getStaffsInRange(rangeSchema=rangeSchema)
        # Getting staffs data by identites
        elif request.args.getlist("identities") is not None and len(request.args.getlist("identities")) > 0:
            identitiesSchema = StaffIdentitiesSchema(identities=request.args.getlist("identities"))
            staffData = StaffService.getStaffsByIdentities(
                identitiesSchema=identitiesSchema)
        # Getting all staffs data
        else:
            staffData: Dict[int, Dict[str, Any]] = StaffService.getAllStaffs()
    except PermissionError as exception:
        return {
            "error":        type(exception).__name__,
            "description":  exception.args[0]
        }, 401
    except ValidationError as exception:
        return {
            "error": "InvalidRequestParameters",
            "description": "Request's parameter format is invalid or contains invalid value"
        }, 400
    except KeyError as exception:
        return {
            "error": "StaffNotFound",
            "description": exception.args[0]
        }, 404
    else:
        response = jsonify(staffData)
        return response
    
@application.route("/api/staffs/<int:identity>", methods=["GET"])
@authenticationRequired
def gettingStaff(identity: int):
    # Validate identity value
    try:
        identitySchema = StaffIdentitySchema(identity=identity)
    except ValidationError:
        return {
            "error": "ValidationError",
            "description": "Staff identity is invalid"
        }, 400
    # Staff identity is validated successfully
    try:
        staffData = StaffService.getStaffByIdentity(identitySchema)
    except PermissionError as exception:
        return {
            "error": "PermissionError",
            "description": exception.args[0]
        }, 401
    except KeyError as exception:
        return {
            "error": "StaffNotFound",
            "description": exception.args[0]
        }, 404
    return staffData
    
@application.route("/api/staffs", methods=["POST"])
@JSONRequestRequired(schema=StaffEntireSchema)
@authenticationRequired
def creatingStaff(requestData: StaffEntireSchema):
    try:
        createdStaffData: Dict[str, Any] = StaffService.createStaff(
            creatingSchema=requestData)
    except PermissionError as exception:
        return {
            "error": type(exception).__name__,
            "description": exception.args[0],
        }, 401
    except SQLModelValidationError as exception:
        return {
            "error": "ValidationError",
            "description": exception.args[0]
        }, 400
    else:
        return createdStaffData
    
@application.route("/api/staffs/<int:updatingIdentity>", methods=["PATCH", "PUT"])
@JSONRequestRequired(schema=StaffPartialSchema)
@authenticationRequired
def updatingStaff(requestedData: StaffPartialSchema, updatingIdentity: int):
    # Validate updating identity argument in the request
    try:
        updatingIdentitySchema = StaffIdentitySchema(identity=updatingIdentity)
    except ValueError:
        return {
            "error": "InvalidRequestArgument",
            "description": "Value for request's parameter 'updatingIdentity' is invalid"
        }, 400
    # Arguement updatingIdentity validated successfully
    updatedStaffInfo: Dict[str, Any]
    try:
        updatedStaffInfo = StaffService.updateStaff(
            updatingIdentity=updatingIdentitySchema.identity,
            updatingSchema=requestedData)
    except PermissionError as exception:
        return {
            "error": type(exception).__name__,
            "description": exception.args[0],
        }, 401
    except SQLModelValidationError as exception:
        return {
            "error": "ValidationError",
            "description": exception.args[0]
        }, 400
    else:
        return jsonify(updatedStaffInfo)

@application.route("/api/staffs/<int:deletingIdentity>", methods=["DELETE"])
@authenticationRequired
def deleteStaff(deletingIdentity: int):
    # Validate updating identity argument in the request
    try:
        deletingIdentitySchema = StaffIdentitySchema(identity=deletingIdentity)
    except ValueError:
        return {
            "error": "InvalidRequestArgument",
            "description": "Value for request's parameter 'deletingIdentity' is invalid"
        }, 400
    # Arguement updatingIdentity validated successfully
    try:
        deletedStaffInfo = StaffService.deleteStaff(
            deletingIdentity=deletingIdentitySchema.identity)
    except PermissionError as exception:
        return {
            "error": type(exception).__name__,
            "description": exception.args[0]
        }, 401
    except KeyError as exception:
        return {
            "error": type(exception).__name__,
            "description": exception.args[0]
        }, 404
    else:
        return deletedStaffInfo