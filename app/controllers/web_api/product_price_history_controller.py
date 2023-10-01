from app import application
from flask import *
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.schemas.product_schema import ProductIdentitySchema
from app.schemas.product_price_history_schema import (
    ProductPriceHistoryPartialSchema,
    ProductPriceHistoryRangeSchema,
    ProductPriceHistoryIdentitiesSchema,
    ProductPriceHistoryIdentitySchema)
from app.services.authentication_service import authenticationRequired
from app.services.product_price_history_service import ProductPriceHistoryService
from app.services.request_validation_service import JSONRequestRequired
from app.errors import NATSException, RequestValidationError
from pydantic import ValidationError
from typing import Dict, Any

@application.route("/api/productPriceHistories", methods=["GET"])
@authenticationRequired
def gettingMultipleProductPriceHistories():
    historiesData: Dict[int, Dict[str, Any]]
    try:
        # Getting product price histories in range
        if request.args.get("startingIdentity") is not None:
            limit = None
            if request.args.get("limit") != 0:
                limit = request.args.get("limit")
            rangeSchema = ProductPriceHistoryRangeSchema(
                startingIdentity=request.args.get("startingIdentity"),
                limit=limit)
            historiesData = ProductPriceHistoryService.getProductPriceHistoriesInRange(
                rangeSchema=rangeSchema)
        # Getting product price histories by identities
        elif request.args.getlist("identities") is not None and len(request.args.getlist("identities")) > 0:
            print(request.args.getlist("identities"))
            identitiesSchema = ProductPriceHistoryIdentitiesSchema(
                identities=request.args.getlist("identities"))
            historiesData = ProductPriceHistoryService.getProductPriceHistoryByIdentities(
                identitiesSchema=identitiesSchema)
        # Getting product price histories by product identity
        elif request.args.get("productIdentity") is not None:
            productIdentitySchema = ProductIdentitySchema(
                identity=request.args.get("productIdentity"))
            historiesData = ProductPriceHistoryService.getProductPriceHistoriesByProductIdentity(
                productIdentity=productIdentitySchema.identity)
        # Getting all product price histories
        else:
            historiesData = ProductPriceHistoryService.getAllProductPriceHistories()
    except (NATSException, ValidationError) as exception:
        if isinstance(exception, ValidationError):
            print(exception)
            return RequestValidationError(exception=exception).toJSONResponse()
        return exception.toJSONResponse()
    else:
        return historiesData
    
@application.route("/api/productPriceHistories/<int:identity>", methods=["GET"])
@authenticationRequired
def gettingProductPriceHistoryByIdentity(identity: int):
    # Validate identity value
    try:
        identitySchema = ProductPriceHistoryIdentitySchema(identity=identity)
    except ValidationError as exception:
        return RequestValidationError(
            modelName="product",
            exception=exception).toJSONResponse()
    # Product price history identity is validated successfully
    historyData: Dict[int, Dict[str, Any]]
    try:
        historyData = ProductPriceHistoryService.getProductPriceHistoryByIdentity(
            identitySchema=identitySchema)
    except NATSException as exception:
        return exception.toJSONResponse()
    else:
        return historyData
    
@application.route("/api/productPriceHistories/<int:identity>", methods=["PUT", "PATCH"])
@JSONRequestRequired(schema=ProductPriceHistoryPartialSchema)
@authenticationRequired
def updatingProductPriceHistory(updatingSchema: ProductPriceHistoryPartialSchema, identity: int):
    # Validating identity value
    try:
        identitySchema = ProductPriceHistoryIdentitySchema(identity=identity)
    except ValidationError as exception:
        return RequestValidationError(
            modelName="productPriceHistory",
            exception=exception).toJSONResponse()
    # Product price history identity has been validated successfully
    try:
        updatedHistoryData = ProductPriceHistoryService.updateProductPriceHistory(
            updatingIdentity=identitySchema.identity,
            updatingSchema=updatingSchema)
    except NATSException as exception:
        return exception.toJSONResponse()
    else:
        return updatedHistoryData
    
@application.route("/api/productPriceHistories/<int:identity>", methods=["DELETE"])
@authenticationRequired
def deletingProductPriceHistory(identity: int):
    # Validate identity value
    try:
        identitySchema = ProductPriceHistoryIdentitySchema(identity=identity)
    except ValidationError as exception:
        return RequestValidationError(
            modelName="product",
            exception=exception).toJSONResponse()
    # Product price history identity has been validated successfully
    try:
        deletedhistoryData = ProductPriceHistoryService.deleteProductPriceHistory(
            deletingIdentity=identitySchema.identity)
    except NATSException as exception:
        return exception.toJSONResponse()
    else:
        return deletedhistoryData
