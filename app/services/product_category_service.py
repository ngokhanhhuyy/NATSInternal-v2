from sqlalchemy.orm import Query
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.product_category_schema import (
    ProductCategorySchema,
    ProductCategoryRangeSchema,
    ProductCategoryIdentitiesSchema,
    ProductCategoryIdentitySchema)
from app.data import session
from app.models.user import User
from app.models.activity import StaffActivity
from app.models.product_category import ProductCategory
from app.services.request_validation_service import UNASSIGNED
from app.services.authorization_service import permissionRequired
from app.services.user_activity_service import activityLogging
from app.validation import SQLModelValidationError
from typing import Union, List, Dict, Optional, Any

class ProductCategoryService:
    @classmethod
    def dictionarySerializing(
        cls,
        productCategories: List[ProductCategory]
    ) -> Dict[int, Dict[str, Any]]:
        productCategoryData: Dict[int, Dict[str, str]] = {}
        if len(list(productCategories)) == 0:
            return productCategoryData
        for productCategory in productCategories:
            productCategoryData[productCategory.identity] = {
                "name":             productCategory.name,
                "isDefault":        productCategory.isDefault,
                "createdDateTime":  productCategory.createdDateTime.isoformat()
            }
        return productCategoryData
    
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Collaborator)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def getAllProductCategories(cls) -> Dict[int, Dict[str, str]]:
        """
            Getting all product categories data as a 
            dictionary ordered by identity ascendingly.
        """
        productCategories: List[ProductCategory] = (
            session.query(ProductCategory)
            .order_by(ProductCategory.identity)
            .all())
        return cls.dictionarySerializing(productCategories=productCategories)
    
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Collaborator)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def getProductCategoriesInRange(cls, rangeSchema: ProductCategoryRangeSchema) -> Dict[int, Dict[str, Any]]:
        """
            Getting product categories data as a dictionary ordered by identity ascendingly in given range.\n
            Each element contains <key> as identity and <value> as a dictionary which contains
            other fields of the product category.\n
            getProductCategoriesInRange(statingIdentity = 1, limit = 5)\n
            => Returning product categories which identities are [1, 2, 3, 4, 5].
        """
        productCategories: List[ProductCategory] = (
            session.query(ProductCategory)
            .filter(ProductCategory.identity >= rangeSchema.startingIdentity)
            .order_by(ProductCategory.identity)
            .limit(rangeSchema.limit)
            .all())
        return cls.dictionarySerializing(productCategories=productCategories)
    
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Collaborator)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def getProductCategoriesByIdentities(
        cls,
        identitiesSchema: ProductCategoryIdentitiesSchema
    ) -> Dict[int, Dict[str, Any]]:
        """
            Getting product categories data as a dictionary ordered by identity ascendingly 
            in given identity list.\n
            Each element contains <key> as identity and <value> as a dictionary which contains
            other fields of the product category.\n
            gettingProductCategoriesByIdentities(identities = [1, 2, 3, 4, 5])\n
            => Returning product categories which identities are [1, 2, 3, 4, 5].
        """
        identities = identitiesSchema.identities
        productCategories: List[ProductCategory] = (
            session.query(ProductCategory)
            .filter(ProductCategory.identity.in_(identitiesSchema.identities))
            .order_by(ProductCategory.identity)
            .all())
        for identity in identities:
            if identity not in [productCategory.identity for productCategory in productCategories]:
                raise KeyError(f"Product category which has identity {identity} cannot be found")
        return cls.dictionarySerializing(productCategories=productCategories)
    
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Collaborator)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def getProductCategoryByIdentity(
        cls,
        identitySchema: ProductCategoryIdentitySchema
    ) -> Dict[int, Dict[str, Any]]:
        """
            Getting product category by given identity received from clients.
            Returning a dictionary containing only one key-value pair.
            The key is the identity that clients requested, while the value is another 
            dictionary which contains all of the product category's information.
        """
        productCategory = (
            session.query(ProductCategory)
            .filter(ProductCategory.identity == identitySchema.identity)
            .first())
        if productCategory is None:
            raise KeyError(
                f"Product category which has identity {identitySchema.identity} "
                "cannot be found")
        return cls.dictionarySerializing([productCategory])

    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Director)
    @activityLogging(
        category=StaffActivity.Categories.CreatingProductCategories,
        status=StaffActivity.Statuses.Unimportant)
    def createProductCategory(cls, creatingSchema: ProductCategorySchema) -> Dict[str, int]:
        """
            Creating product category with given data received from client.\n
            Returning a dictionary which contains created productCategory identity and name.
        """
        productCategory = ProductCategory()
        try:
            productCategory.name = creatingSchema.name
            productCategory.isDefault = False
            session.add(productCategory)
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise SQLAlchemyError(
                f"Product category name {productCategory.name} has already existed")
        else:
            return {
                "identity": productCategory.identity,
                "name": productCategory.name
            }

    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Director)
    @activityLogging(
        category=StaffActivity.Categories.UpdatingProductCategories,
        status=StaffActivity.Statuses.Important)
    def updatingProductCategory(cls, updatingIdentity: int, updatingSchema: ProductCategorySchema) -> Dict[str, int]:
        """
            Updating product category by identity and data retrieved from clients' requests.
            Returning a dictionary of updated productCategory's identity after updating successfully.
        """
        productCategory: Optional[ProductCategory] = (
            session.query(ProductCategory)
            .filter(ProductCategory.identity == updatingIdentity)
            .first())
        if productCategory is not None:
            productCategory.name = updatingSchema.name
            try:
                session.commit()
            except SQLAlchemyError:
                session.rollback()
                raise SQLModelValidationError(
                    f"Cannot update product category which has identity {updatingIdentity}")
            else:
                return {
                    "identity": productCategory.identity
                }
        else:
            raise KeyError(
                f"Product category which has identity {updatingIdentity} cannot be found")
        
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Director)
    @activityLogging(
        category=StaffActivity.Categories.DeletingProductCategories,
        status=StaffActivity.Statuses.Important)
    def deleteProductCategory(cls, deletingIdentity: int) -> Dict[str, int]:
        """
            Deleting product category by identity retrieved from clients.
            Returning a dictionary of product category's identity after deleting successfully.
        """
        productCategory: Optional[ProductCategory] = (
            session.query(ProductCategory)
            .filter(ProductCategory.identity == deletingIdentity)
            .first())
        if productCategory is not None:
            session.delete(productCategory)
            try:
                session.commit()
            except SQLAlchemyError:
                session.rollback()
                raise SQLModelValidationError(
                    f"Cannot delete product category which has identity {deletingIdentity}")
            else:
                return {
                    "identity": deletingIdentity
                }
        else:
            raise KeyError(
                f"Product category which has identity {deletingIdentity} cannot be found")