from app import application
from flask import *
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.brand_schema import *
from app.services.authentication_service import authenticationRequired
from app.services.brand_service import BrandService
from app.services.request_validation_service import JSONRequestRequired
from app.validation import SQLModelValidationError
from pydantic import ValidationError
from typing import Dict, Any

@application.route("/api/brands", methods=["GET"])
@authenticationRequired
def gettingMutipleProductBrands():
    brandsData: Dict[int, Dict[str, Any]]
    try:
        # Getting brands in range
        if request.args.get("startingIdentity") is not None:
            limit = None
            if request.args.get("limit") != 0:
                limit = request.args.get("limit")
            rangeSchema = BrandRangeSchema(
                startingIdentity=request.args.get("startingIdentity"),
                limit=limit)
            brandsData = BrandService.getBrandsInRange(rangeSchema=rangeSchema)
        # Getting brands by identities
        elif request.args.getlist("identities") is not None and len(request.args.getlist("identities")) > 0:
            identitiesSchema = BrandIdentitiesSchema(
                identities=request.args.getlist("identities"))
            brandsData = BrandService.getBrandsByIdentities(
                identitiesSchema=identitiesSchema)
        # Getting all brands
        else:
            brandsData = BrandService.getAllBrands()
    except PermissionError as exception:
        return {
            "error":        "PermissionError",
            "description":  exception.args[0]
        }, 401
    except ValidationError:
        return {
            "error": "InvalidRequestParameters",
            "description": "Request's parameter format is invalid or contains invalid value"
        }, 400
    except KeyError as exception:
        return {
            "error": "BrandNotFound",
            "description": exception.args[0]
        }, 404
    else:
        return brandsData
    
@application.route("/api/brands/<int:identity>", methods=["GET"])
@authenticationRequired
def gettingBrand(identity: int):
    # Validating identity value
    try:
        identitySchema = BrandIdentitySchema(identity=identity)
    except ValidationError:
        return {
            "error": "ValidationError",
            "description": "Brand identity is invalid"
        }, 400
    # Brand identity is validated successfully
    brandData: Dict[int, Dict[str, Any]]
    try:
        brandData = BrandService.getBrandByIdentity(identitySchema)
    except PermissionError as exception:
        return {
            "error": "PermissionError",
            "description": exception.args[0]
        }, 401
    except KeyError as exception:
        return {
            "error": "BrandNotFound",
            "description": exception.args[0]
        }, 404
    else:
        return brandData

@application.route("/api/brands", methods=["POST"])
@JSONRequestRequired(schema=BrandEntireSchema)
@authenticationRequired
def creatingBrand(creatingSchema: BrandEntireSchema):
    try:
        createdBrandData = BrandService.createBrand(
            creatingSchema=creatingSchema)
    except PermissionError as exception:
        return {
            "error": "PermissionError",
            "description": exception.args[0]
        }, 401
    except (SQLAlchemyError, SQLModelValidationError) as exception:
        return {
            "error": "ValidationError",
            "description": exception.args[0]
        }, 400
    else:
        return createdBrandData

@application.route("/api/brands/<int:identity>", methods=["PUT", "PATCH"])
@JSONRequestRequired(schema=BrandPartialSchema)
@authenticationRequired
def updatingBrand(updatingSchema: BrandPartialSchema, identity: int):
    # Validating identity value:
    try:
        identitySchema = BrandIdentitySchema(identity=identity)
    except ValidationError:
        return {
            "error": "ValidationError",
            "description": "Customer identity is invalid"
        }, 400
    # Brand identity is validated successfully
    updatedBrandInfo: Dict[str, int]
    try:
        updatedBrandInfo = BrandService.updateBrand(
            updatingIdentity=identitySchema.identity,
            updatingSchema=updatingSchema)
    except PermissionError as exception:
        return {
            "error": type(exception).__name__,
            "description": exception.args[0]
        }, 401
    except SQLModelValidationError as exception:
        return {
            "error": "ValidationError",
            "description": exception.args[0]
        }, 400
    except KeyError as exception:
        return {
            "error": "BrandNotFound",
            "description": exception.args[0]
        }, 404
    else:
        return updatedBrandInfo

@application.route("/api/brands/<int:identity>", methods=["DELETE"])
@authenticationRequired
def deletingBrand(identity: int):
    # Validate identity value
    try:
        identitySchema = BrandIdentitySchema(identity=identity)
    except ValidationError:
        return {
            "error": "ValidaitonError",
            "description": "Brand identity is invalid"
        }, 400
    # Brand identity is validated successfully
    try:
        deletedBrandInfo = BrandService.deleteBrand(
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
            "error": "BrandNotFound",
            "description": exception.args[0]
        }, 404
    else:
        return deletedBrandInfo

