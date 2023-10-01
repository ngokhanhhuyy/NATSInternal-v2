from app import application
from flask import *
from app.schemas.customer_schema import (
    CustomerEntireSchema,
    CustomerPartialSchema,
    CustomerRangeSchema,
    CustomerIdentitiesSchema,
    CustomerIdentitySchema)
from app.services.authentication_service import authenticationRequired
from app.services.customer_service import CustomerService
from app.services.request_validation_service import JSONRequestRequired
from app.validation import SQLModelValidationError
from pydantic import ValidationError
from typing import Dict, Any

@application.route("/api/customers", methods=["GET"])
@authenticationRequired
def gettingMultipleCustomers():
    customerData: Dict[int, Dict]
    try:
        # Getting customers in range
        if request.args.get("startingIdentity") is not None:
            rangeSchema = CustomerRangeSchema(
                startingIdentity=request.args.get("startingIdentity"),
                limit=request.args.get("limit") if request.args.get("limit") != 0 else None)
            customerData = CustomerService.getCustomersInRange(rangeSchema=rangeSchema)
        # Getting customers by list of identities
        elif request.args.getlist("identities") is not None and len(request.args.getlist("identities")) > 0:
            identitiesSchema = CustomerIdentitiesSchema(
                identities=request.args.getlist("identities"))
            customerData = CustomerService.getCustomersByIdentities(
                identitiesSchema=identitiesSchema)
        # Getting all customers
        else:
            customerData = CustomerService.getAllCustomers()
    except PermissionError as exception:
        return {
            "error":        type(exception).__name__,
            "description":  exception.args[0]
        }, 401
    except ValidationError:
        return {
            "error": "InvalidRequestParameters",
            "description": "Request's parameter format is invalid or contains invalid value"
        }, 400
    except KeyError as exception:
        return {
            "error": "CustomerNotFound",
            "description": exception.args[0]
        }, 404
    else:
        return customerData

@application.route("/api/customers/<int:identity>", methods=["GET"])
@authenticationRequired
def gettingCustomer(identity: int):
    # Validating identity value
    try:
        identitySchema = CustomerIdentitySchema(identity=identity)
    except ValidationError:
        return {
            "error": "ValidationError",
            "description": "Customer identity is invalid"
        }, 400
    # Customer identity is validated successfully
    customerData: Dict[int, Dict[str, Any]]
    try:
        customerData = CustomerService.getCustomerByIdentity(identitySchema)
    except PermissionError as exception:
        return {
            "error": "PermissionError",
            "description": exception.args[0]
        }, 401
    except KeyError as exception:
        return {
            "error": "CustomerNotFound",
            "description": exception.args[0]
        }, 404
    else:
        return customerData

@application.route("/api/customers", methods=["POST"])
@JSONRequestRequired(schema=CustomerEntireSchema)
@authenticationRequired
def creatingCustomer(requestData: CustomerEntireSchema):
    try:
        createdCustomerData = CustomerService.createCustomer(
            creatingSchema=requestData)
    except PermissionError as exception:
        return {
            "error": "PermissionError",
            "description": exception.args[0]
        }, 401
    except SQLModelValidationError as exception:
        return {
            "error": "ValidationError",
            "description": exception.args[0]
        }, 400
    else:
        return createdCustomerData
    
@application.route("/api/customers/<int:identity>", methods=["PUT", "PATCH"])
@JSONRequestRequired(schema=CustomerPartialSchema)
@authenticationRequired
def updatingCustomer(updatingSchema: CustomerPartialSchema, identity: int):
    # Validating identity value
    try:
        identitySchema = CustomerIdentitySchema(identity=identity)
    except ValidationError:
        return {
            "error": "ValidationError",
            "description": "Customer identity is invalid"
        }, 400
    # Customer identity is validated successfully
    updatedCustomerInfo: Dict[str, int]
    try:
        updatedCustomerInfo = CustomerService.updatingCustomer(
            updatingIdentity=identitySchema.identity,
            updatingSchema=updatingSchema)
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
    except KeyError as exception:
        return {
            "error": "CustomerNotFound",
            "description": exception.args[0],
        }, 404
    else:
        return updatedCustomerInfo
    
@application.route("/api/customers/<int:identity>", methods=["DELETE"])
@authenticationRequired
def deletingCustomer(identity: int):
    # Validate identity value
    try:
        identitySchema = CustomerIdentitySchema(identity=identity)
    except ValidationError:
        return {
            "error": "ValidationError",
            "description": "Customer identity is invalid"
        }, 400
    # Customer identity is validated successfully
    try:
        deletedCustomerData = CustomerService.deleleCustomer(
            deletingIdentity=identitySchema.identity)
    except PermissionError as exception:
        return {
            "error": "PermissionError",
            "description": exception.args[0]
        }, 401
    except SQLModelValidationError as exception:
        return {
            "error": "ValidationError",
            "description": exception.args[0]
        }, 400
    except KeyError as exception:
        return {
            "error": "CustomerNotFound",
            "description": exception.args[0]
        }, 404
    else:
        return deletedCustomerData