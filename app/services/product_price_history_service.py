from sqlalchemy.orm import Query
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from psycopg2.errors import ForeignKeyViolation
from app.schemas.product_price_history_schema import *
from app.data import session
from app.models.user import User
from app.models.activity import StaffActivity
from app.models.product_price_history import ProductPriceHistory
from app.models.product import Product
from app.services.request_validation_service import UNASSIGNED
from app.services.authorization_service import permissionRequired
from app.services.user_activity_service import activityLogging
from app.validation import SQLModelValidationError
from app.errors import ErrorCodes, DataValidationError, DataOperationError, NotFoundError
from typing import Union, List, Dict, Tuple, Optional, Any
from pydantic import ValidationError

class ProductPriceHistoryService:
    @classmethod
    def dictionarySerializing(
        cls,
        histories: List[ProductPriceHistory]
    ) -> Dict[int, Dict[str, Any]]:
        historiesData: Dict[int, Dict[str, Any]] = {}
        if len(list(histories)) == 0:
            return historiesData
        for history in histories:
            historiesData[history.identity] = {
                "identity":         history.identity,
                "productIdentity":  history.productIdentity,
                "publishedPrice":   history.publishedPrice,
                "vatFactor":        history.vatFactor,
                "loggedDateTime":   history.loggedDateTime,
                "changedType":      history.changedType
            }
        return historiesData
    
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Collaborator)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def getAllProductPriceHistories(cls) -> Dict[int, Dict[str, Any]]:
        """
            Getting all product price histories as a dictionary 
            ordered by identity ascendingly.
        """
        histories: List[ProductPriceHistory] = (
            session.query(ProductPriceHistory)
            .order_by(ProductPriceHistory.identity)
            .all())
        return cls.dictionarySerializing(histories=histories)
    
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Collaborator)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def getProductPriceHistoriesInRange(
        cls,
        rangeSchema: ProductPriceHistoryRangeSchema
    ) -> Dict[int, Dict[str, Any]]:
        """
            Getting product price histories as a dictionary ordered by identities 
            acendingly in given range.\n
            Each element contains <key> as identity and <value> as another dictionary 
            which contains other fields of the product price history.\n
            getProductsPriceHistoryInRange(startingIdentity = 1, limit = 5)\n
            => Returning product price histories which identities are [1, 2, 3, 4, 5].
        """
        histories: List[ProductPriceHistory] = (
            session.query(ProductPriceHistory)
            .filter(ProductPriceHistory.identity >= rangeSchema.startingIdentity)
            .order_by(ProductPriceHistory.identity)
            .limit(rangeSchema.limit)
            .all())
        return cls.dictionarySerializing(histories=histories)

    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Collaborator)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def getProductPriceHistoryByIdentities(
        cls,
        identitiesSchema: ProductPriceHistoryIdentitiesSchema
    ) -> Dict[int, Dict[str, Any]]:
        """
            Getting product price histories as a dictionary ordered by identity ascendingly
            in given identity list.\n
            Each element contains <key> as identity and <value> as a dictionary which contains
            other fields of the product price history.\n
            gettingProductPriceHistoriesByIdentities(identity = [1, 2, 3, 4, 5])\n
            => Returning product price histories which identities are [1, 2, 3, 4, 5].
        """
        identities = identitiesSchema.identities
        histories: List[ProductPriceHistory] = (
            session.query(ProductPriceHistory)
            .filter(ProductPriceHistory.identity.in_(identities))
            .all())
        for identity in identities:
            if identity not in [history.identity for history in histories]:
                raise NotFoundError(
                    modelName=ProductPriceHistory.__tablename__,
                    identity=identity)
        return cls.dictionarySerializing(histories=histories)
    
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Collaborator)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def getProductPriceHistoryByIdentity(
        cls,
        identitySchema: ProductPriceHistoryIdentitySchema
    ) -> Dict[int, Dict[str, Any]]:
        """
            Getting product price history by given identity received from clients.
            Returning a dictionary containing only one key-value pair.
            The key is the identity that clients requested, while the value is another
            dictionary which contains all of the product price history's information.
        """
        history = (
            session.query(ProductPriceHistory)
            .filter(ProductPriceHistory.identity == identitySchema.identity)
            .first())
        if history is None:
            raise NotFoundError(
                modelName=ProductPriceHistory.__tablename__,
                identity=identitySchema.identity)
        return cls.dictionarySerializing([history])
    
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Collaborator)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def getProductPriceHistoriesByProductIdentity(
        cls,
        productIdentity: int
    ) -> Dict[int, Dict[str, Any]]:
        """
            Getting product price history by given product identity received from clients.
        """
        # Validate if given product identity is existing
        productCount = session.query(Product).count()
        if productCount == 0:
            raise NotFoundError(
                modelName=Product.__tablename__,
                identity=productIdentity)
        else:
            histories: List[ProductPriceHistory] = (
                session.query(ProductPriceHistory)
                .filter(ProductPriceHistory.productIdentity == productIdentity)
                .order_by(ProductPriceHistory.loggedDateTime)
                .all())
            return cls.dictionarySerializing(histories=histories)
        
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Director)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def updateProductPriceHistory(
        cls,
        updatingIdentity: int,
        updatingSchema: ProductPriceHistoryPartialSchema
    ) -> Dict[int, Dict[str, Any]]: 
        """
            Updating product price history by identity and data retrieved from
            clients' requests.
            Returning a dictionary of updated product price history's identity
            after updating successfully.
        """
        history: Optional[ProductPriceHistory] = (
            session.query(ProductPriceHistory)
            .filter(ProductPriceHistory.identity == updatingIdentity)
            .first())
        if history is not None:
            for field, value in updatingSchema.dict().items():
                if value != UNASSIGNED:
                    setattr(history, field, value)
            try:
                session.commit()
            except IntegrityError as exception:
                session.rollback()
                raise DataOperationError(exception=exception)
            else:
                return {
                    "identity": history.identity
                }
        else:
            raise NotFoundError(
                modelName=ProductPriceHistory.__tablename__,
                identity=updatingIdentity)
        
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Director)
    @activityLogging(
        category=StaffActivity.Categories.DeletingProductPriceHistories,
        status=StaffActivity.Statuses.Important)
    def deleteProductPriceHistory(cls, deletingIdentity: int) -> Dict[str, int]:
        """
            Deleting product price history by identity retrieved from clients.
            Returning a dictionary of product's identity after deleting successfully.
        """
        history: Optional[ProductPriceHistory] = (
            session.query(ProductPriceHistory)
            .filter(ProductPriceHistory.identity == deletingIdentity)
            .first())
        if history is not None:
            session.delete(history)
            try:
                session.commit()
            except IntegrityError as exception:
                session.rollback()
                raise DataOperationError(exception=exception)
            else:
                return {
                    "identity": history.identity
                }
        else:
            raise NotFoundError(
                modelName=ProductPriceHistory.__tablename__,
                identity=deletingIdentity)

    