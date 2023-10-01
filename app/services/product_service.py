from sqlalchemy.orm import Query
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from psycopg2.errors import ForeignKeyViolation
from app.schemas.product_schema import (
    ProductEntireSchema,
    ProductPartialSchema,
    ProductRangeSchema,
    ProductIdentitiesSchema,
    ProductIdentitySchema)
from app.data import session
from app.models.user import User
from app.models.activity import StaffActivity
from app.models.product import Product
from app.services.request_validation_service import UNASSIGNED
from app.services.authorization_service import permissionRequired
from app.services.user_activity_service import activityLogging
from app.errors import ErrorCodes, DataValidationError, DataOperationError, NotFoundError
from typing import Union, List, Dict, Tuple, Optional, Any
from pydantic import ValidationError

class ProductService:
    @classmethod
    def dictionarySerializing(
        cls,
        products: List[Product]
    ) -> Dict[int, Dict[str, Any]]:
        productData: Dict[int, Dict[str, Any]] = {}
        if len(list(products)) == 0:
            return productData
        for product in products:
            productData[product.identity] = {
                "name":                 product.name,
                "brandIdentity":        product.brandIdentity,
                "categoryIdentity":     product.categoryIdentity,
                "description":          product.description,
                "unit":                 product.unit,
                "createdDateTime":      product.createdDateTime,
                "updatedDateTime":      product.updatedDateTime,
                "thumbnail":            product.thumbnail,
                "photos":               product.photos
            }
        return productData

    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Collaborator)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def getAllProducts(cls) -> Dict[int, Dict[str, Any]]:
        """
            Getting all product data as a 
            dictionary ordered by identity ascendingly.
        """
        products: List[Product] = (
            session.query(Product)
            .order_by(Product.identity)
            .all())
        return cls.dictionarySerializing(products=products)

    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Collaborator)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def getProductsInRange(cls, rangeSchema: ProductRangeSchema) -> Dict[int, Dict[str, Any]]:
        """
            Getting products data as a dictionary ordered by identities ascendingly in given range.\n
            Each element contains <key> as identity and <value> as a dictionary which contains
            other fields of the product.\n
            getProductsInRange(startingIdentity = 1, limit = 5)\n
            => Returning products which identities are [1, 2, 3, 4, 5].
        """
        products: List[Product] = (
            session.query(Product)
            .filter(Product.identity >= rangeSchema.startingIdentity)
            .order_by(Product.identity)
            .limit(rangeSchema.limit)
            .all())
        return cls.dictionarySerializing(products=products)
    
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Collaborator)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def getProductsByIdentities(
        cls,
        identitiesSchema: ProductIdentitiesSchema
    ) -> Dict[int, Dict[str, Any]]:
        """
            Getting products data as a dictionary ordered by identity ascendingly 
            in given identity list.\n
            Each element contains <key> as identity and <value> as a dictionary which contains
            other fields of the product category.\n
            gettingProductByIdentities(identities = [1, 2, 3, 4, 5])\n
            => Returning products which identities are [1, 2, 3, 4, 5].
        """
        products: List[Product] = (
            session.query(Product)
            .filter(Product.identity.in_(identitiesSchema.identities))
            .order_by(Product.identity)
            .all())
        for identity in identitiesSchema.identities:
            if identity not in [product.identity for product in products]:
                raise NotFoundError(
                    modelName=Product.__tablename__,
                    identity=identity)
        return cls.dictionarySerializing(products=products)
    
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Collaborator)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def getProductByIdentity(
        cls,
        identitySchema: ProductIdentitySchema
    ) -> Dict[int, Dict[str, Any]]:
        """
            Getting product by given identity received from clients.
            Returning a dictionary containing only one key-value pair.
            The key is the identity that clients requested, while the value is another 
            dictionary which contains all of the product's information.
        """
        product = (
            session.query(Product)
            .filter(Product.identity == identitySchema.identity)
            .first())
        if product is None:
            raise NotFoundError(
                modelName=Product.__tablename__,
                identity=identitySchema.identity)
        return cls.dictionarySerializing([product])
    
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Director)
    @activityLogging(
        category=StaffActivity.Categories.CreatingProducts,
        status=StaffActivity.Statuses.Unimportant)
    def createProduct(cls, creatingSchema: ProductEntireSchema) -> Dict[str, Any]:
        """
            Creating product with given data received from client.\n
            Returning a dictionary which contains created product identity and name.
        """
        product = Product()
        try:
            product.name = creatingSchema.name
            product.brandIdentity = creatingSchema.brandIdentity
            product.categoryIdentity = creatingSchema.categoryIdentity
            product.description = creatingSchema.description
            product.unit = creatingSchema.unit
            product.publishedPrice = creatingSchema.publishedPrice
            product.vatFactor = creatingSchema.vatFactor
            product.thumbnail = creatingSchema.thumbnail
            product.photos = creatingSchema.photos
            session.add(product)
            session.commit()
        except IntegrityError as exception:
            session.rollback()
            raise DataOperationError(exception=exception)
        else:
            return {
                "identity": product.identity,
                "name": product.name
            }
        
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Director)
    @activityLogging(
        category=StaffActivity.Categories.UpdatingProducts,
        status=StaffActivity.Statuses.Important)
    def updateProduct(
        cls,
        updatingIdentity: int,
        updatingSchema: ProductPartialSchema
    ) -> Dict[int, Dict[str, Any]]:
        """
            Updating product by identity and data retrieved from clients' requests.
            Returning a dictionary of updated product's identity after updating successfully.
        """
        product: Optional[Product] = (
            session.query(Product)
            .filter(Product.identity == updatingIdentity)
            .first())
        if product is not None:
            for field, value in updatingSchema.dict().items():
                if value != UNASSIGNED:
                    setattr(product, field, value)
            try:
                session.commit()
            except IntegrityError as exception:
                session.rollback()
                raise DataOperationError(exception=exception)
            else:
                return {
                    "identity": product.identity
                }
        else:
            raise NotFoundError(
                modelName=Product.__tablename__,
                identity=updatingIdentity)
        
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Director)
    @activityLogging(
        category=StaffActivity.Categories.DeletingProducts,
        status=StaffActivity.Statuses.Important)
    def deleteProduct(cls, deletingIdentity: int) -> Dict[str, int]:
        """
            Deleting product by identity retrieved from clients.
            Returning a dictionary of product's identity after deleting successfully.
        """
        product: Optional[Product] = (
            session.query(Product)
            .filter(Product.identity == deletingIdentity)
            .first())
        if product is not None:
            session.delete(product)
            try:
                session.commit()
            except IntegrityError as exception:
                session.rollback()
                raise DataOperationError(exception=exception)
            else:
                return {
                    "identity": product.identity
                }
        else:
            raise NotFoundError(
                modelName=Product.__tablename__,
                identity=deletingIdentity)