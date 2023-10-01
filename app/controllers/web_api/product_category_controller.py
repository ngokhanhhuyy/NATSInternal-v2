from app import application
from flask import *
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.product_category_schema import *
from app.services.authentication_service import authenticationRequired
from app.services.product_category_service import ProductCategoryService
from app.services.request_validation_service import JSONRequestRequired
from app.validation import SQLModelValidationError
from pydantic import ValidationError
from typing import Dict, Any

@application.route("/api/productCategories", methods=["GET"])
@authenticationRequired
def gettingMultipleProductCategories():
    categoriesData: Dict[int, Dict[str, Any]]
    try:
        # Getting product categories in range
        if request.args.get("startingIdentity") is not None:
            limit = None
            if request.args.get("limit") != 0:
                limit = request.args.get("limit")
            rangeSchema = ProductCategoryRangeSchema(
                startingIdentity=request.args.get("startingIdentity"),
                limit=limit)
            categoriesData = ProductCategoryService.getProductCategoriesInRange(
                rangeSchema=rangeSchema)
        # Getting product categories by identities
        elif request.args.getlist("identities") is not None and len(request.args.getlist("identities")) > 0:
            identitiesSchema = ProductCategoryIdentitiesSchema(
                identities=request.args.getlist("identities"))
            categoriesData = ProductCategoryService.getProductCategoriesByIdentities(
                identitiesSchema=identitiesSchema)
        # Getting all product categories
        else:
            categoriesData = ProductCategoryService.getAllProductCategories()
    except PermissionError as exception:
        return {
            "error":        "PermissionError",
            "description":  exception.args[0]
        }, 401
    except ValidationError:
        return {
            "error":        "InvalidRequestParameters",
            "description":  "Request's parameter format is invalid or contains invalid value"
        }, 400
    except KeyError as exception:
        return {
            "error":        "ProductCategoryNotFound",
            "description":  exception.args[0]
        }, 404
    else:
        return categoriesData
    
@application.route("/api/productCategories/<int:identity>", methods=["GET"])
@authenticationRequired
def gettingProductCategory(identity: int):
    # Validating identity value
    try:
        identitySchema = ProductCategoryIdentitySchema(identity=identity)
    except ValidationError:
        return {
            "error": "ValidationError",
            "description": "Product category identity is invalid"
        }, 400
    # Product category identity is validated successfully
    productCategoryData: Dict[int, Dict[str, Any]]
    try:
        productCategoryData = ProductCategoryService.getProductCategoryByIdentity(identitySchema)
    except PermissionError as exception:
        return {
            "error": "PermissionError",
            "description": exception.args[0]
        }, 401
    except KeyError as exception:
        return {
            "error": "ProductCategoryNotFound",
            "description": exception.args[0]
        }, 404
    else:
        return productCategoryData
        
@application.route("/api/productCategories", methods=["POST"])
@JSONRequestRequired(schema=ProductCategorySchema)
@authenticationRequired
def creatingProductCategory(creatingSchema: ProductCategorySchema):
    try:
        createdProductCategoryData = ProductCategoryService.createProductCategory(
            creatingSchema=creatingSchema)
    except PermissionError as exception:
        return {
            "error": "PermissionError",
            "description": exception.args[0]
        }, 401
    except (SQLAlchemyError, SQLModelValidationError) as exception:
        return {
            "error": "ValidationError",
            "descrption": exception.args[0]
        }, 400
    else:
        return createdProductCategoryData
    
@application.route("/api/productCategories/<int:identity>", methods=["PUT", "PATCH"])
@JSONRequestRequired(schema=ProductCategorySchema)
@authenticationRequired
def updatingProductCateory(updatingSchema: ProductCategorySchema, identity: int):
    # Validating identity value:
    try:
        identitySchema = ProductCategoryIdentitySchema(identity=identity)
    except ValidationError:
        return {
            "error": "ValidationError",
            "description": "Product category identity is invalid"
        }, 400
    # Product category is validated successfully
    updatedProductCategoryData: Dict[str, int]
    try:
        updatedProductCategoryData = ProductCategoryService.updatingProductCategory(
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
            "error": "ProductCategoryNotFound",
            "description": exception.args[0]
        }, 404
    else:
        return updatedProductCategoryData
    
@application.route("/api/productCategories/<int:identity>", methods=["DELETE"])
@authenticationRequired
def deletingProductCategory(identity: int):
    # Validate identity value
    try:
        identitySchema = ProductCategoryIdentitySchema(identity=identity)
    except ValidationError:
        return {
            "error": "ValidationError",
            "description": "Product category identity is invalid"
        }, 400
    # Product category identity is validated successfully
    deletedProductCategoryInfo: Dict[str, int]
    try:
        deletedProductCategoryInfo = ProductCategoryService.deleteProductCategory(
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
            "error": "ProductCategoryNotFound",
            "description": exception.args[0]
        }, 404
    else:
        return deletedProductCategoryInfo