from app import application
from flask import *
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.schemas.product_schema import (
    ProductEntireSchema,
    ProductPartialSchema,
    ProductRangeSchema,
    ProductIdentitiesSchema,
    ProductIdentitySchema)
from app.services.authentication_service import authenticationRequired
from app.services.product_service import ProductService
from app.services.request_validation_service import JSONRequestRequired
from app.errors import NATSException, RequestValidationError
from pydantic import ValidationError
from typing import Dict, Any

@application.route("/api/products", methods=["GET"])
@authenticationRequired
def gettingMultipleProducts():
    productsData: Dict[int, Dict[str, Any]]
    try:
        # Getting products in range
        if request.args.get("startingIdentity") is not None:
            limit = None
            if request.args.get("limit") != 0:
                limit = request.args.get("limit")
            rangeSchema = ProductRangeSchema(
                startingIdentity=request.args.get("startingIdentity"),
                limit=limit)
            productsData = ProductService.getProductsInRange(
                rangeSchema=rangeSchema)
        # Getting products by identities
        elif request.args.getlist("identities") is not None and len(request.args.getlist("identities")) > 0:
            identitiesSchema = ProductIdentitiesSchema(
                identities=request.args.getlist("identities"))
            productsData = ProductService.getProductsByIdentities(
                identitiesSchema=identitiesSchema)
        # Getting all products
        else:
            productsData = ProductService.getAllProducts()
    except NATSException as exception:
        return exception.toJSONResponse()
    else:
        return productsData
    
@application.route("/api/products/<int:identity>", methods=["GET"])
@authenticationRequired
def gettingProductByIdentity(identity: int):
    # Validate identity value
    try:
        identitySchema = ProductIdentitySchema(identity=identity)
    except ValidationError as exception:
        return RequestValidationError(
            modelName="product",
            exception=exception).toJSONResponse()
    # Product identity is validated successfully
    productData: Dict[int, Dict[str, Any]]
    try:
        productData = ProductService.getProductByIdentity(identitySchema)
    except NATSException as exception:
        return exception.toJSONResponse()
    else:
        return productData
    
@application.route("/api/products", methods=["POST"])
@JSONRequestRequired(schema=ProductEntireSchema)
@authenticationRequired
def createProduct(creatingSchema: ProductEntireSchema):
    try:
        createdProductData = ProductService.createProduct(
            creatingSchema=creatingSchema)
    except NATSException as exception:
        return exception.toJSONResponse()
    else:
        return createdProductData
    
@application.route("/api/products/<int:identity>", methods=["PUT", "PATCH"])
@JSONRequestRequired(schema=ProductPartialSchema)
@authenticationRequired
def updatingProduct(updatingSchema: ProductPartialSchema, identity: int):
    # Validating identity value
    try:
        identitySchema = ProductIdentitySchema(identity=identity)
    except ValidationError as exception:
        return RequestValidationError(
            modelName="product",
            exception=exception).toJSONResponse()
    # Product identity is validated successfully
    updatedProductData: Dict[str, int]
    try:
        updatedProductData = ProductService.updateProduct(
            updatingIdentity=identitySchema.identity,
            updatingSchema=updatingSchema)
    except NATSException as exception:
        return exception.toJSONResponse()
    else:
        return updatedProductData
    
@application.route("/api/products/<int:identity>", methods=["DELETE"])
@authenticationRequired
def deletingProduct(identity: int):
    # Validate identity value
    try:
        identitySchema = ProductIdentitySchema(identity=identity)
    except ValidationError as exception:
        return RequestValidationError(
            modelName="product",
            exception=exception).toJSONResponse()
    # Product identity is validated successfully
    deletedProductData: Dict[str, int]
    try:
        deletedProductData = ProductService.deleteProduct(
            deletingIdentity=identitySchema.identity)
    except NATSException as exception:
        return exception.toJSONResponse()
    else:
        return deletedProductData

