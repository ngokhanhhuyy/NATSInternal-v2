from sqlalchemy.orm import Query
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.brand_schema import (
    BrandEntireSchema,
    BrandIdentitiesSchema,
    BrandIdentitySchema,
    BrandPartialSchema,
    BrandRangeSchema,)
from app.data import session
from app.models.user import User
from app.models.activity import StaffActivity
from app.models.brand import Brand
from app.services.request_validation_service import UNASSIGNED
from app.services.authorization_service import permissionRequired
from app.services.user_activity_service import activityLogging
from app.validation import SQLModelValidationError
from typing import Union, List, Dict, Optional, Any

class BrandService:
    @classmethod
    def dictionarySerializing(
        cls,
        brands: Union[List[Brand], Query[Brand]]
    ) -> Dict[int, Dict[str, Any]]:
        brandData: Dict[int, Dict[str, Any]] = {}
        if len(list(brands)) == 0:
            return brandData
        for brand in brands:
            logo = None
            if brand.logo is not None:
                logo = brand.logo.decode()
            photos = None
            if brand.photos is not None:
                photos = []
                for photo in brand.photos:
                    photos.append(photo)
            brandData[brand.identity] = {
                "logo":             logo,
                "name":             brand.name,
                "countryCode":      brand.countryCode,
                "website":          brand.website,
                "socialMediaURL":   brand.socialMediaURL,
                "phone":            brand.phone,
                "email":            brand.email,
                "address":          brand.address,
                "photos":           photos
            }
        return brandData
    
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Collaborator)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def getAllBrands(cls) -> Dict[int, Dict[str, str]]:
        """
            Getting all product brands data as a dictionary ordered by identity ascendingly.
        """
        brands: List[Brand] = (
            session.query(Brand)
            .order_by(Brand.identity)
            .all())
        return cls.dictionarySerializing(brands=brands)
    
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Collaborator)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def getBrandsInRange(cls, rangeSchema: BrandRangeSchema) -> Dict[int, Dict[str, Any]]:
        """
            Getting brands data as a dictionary ordered by identity ascendingly in given range.\n
            Each element contains <key> as identity and <value> as a dictionary which contains
            other fields of the brand.\n
            getBrandsInRange(statingIdentity = 1, limit = 5)\n
            => Returning brands which identities are [1, 2, 3, 4, 5].
        """
        brands: List[Brand] = (
            session.query(Brand)
            .filter(Brand.identity >= rangeSchema.startingIdentity)
            .order_by(Brand.identity)
            .limit(rangeSchema.limit)
            .all())
        return cls.dictionarySerializing(brands=brands)
    
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Collaborator)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def getBrandsByIdentities(cls, identitiesSchema: BrandIdentitiesSchema) -> Dict[int, Dict[str, Any]]:
        """
            Getting brands data as a dictionary ordered by identity ascendingly in given identity list.\n
            Each element contains <key> as identity and <value> as a dictionary which contains
            other fields of the brand.\n
            gettingBrandsByIdentities(identities = [1, 2, 3, 4, 5])\n
            => Returning brands which identities are [1, 2, 3, 4, 5].
        """
        identities = identitiesSchema.identities
        brands: List[Brand] = (
            session.query(Brand)
            .filter(Brand.identity.in_(identitiesSchema.identities))
            .order_by(Brand.identity)
            .all())
        for identity in identities:
            if identity not in [brand.identity for brand in brands]:
                raise KeyError(f"Brand which has identity {identity} cannot be found")
        return cls.dictionarySerializing(brands=brands)
    
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Collaborator)
    @activityLogging(
        category=StaffActivity.Categories.SendingRequest,
        status=StaffActivity.Statuses.Unimportant)
    def getBrandByIdentity(cls, identitySchema: BrandIdentitySchema) -> Dict[int, Dict[str, Any]]:
        """
            Getting brand by given identity received from clients.
            Returning a dictionary containing only one key-value pair.
            The key is the identity that clients requested, while the value is another 
            dictionary which contains all of the brand's information.
        """
        brand = (
            session.query(Brand)
            .filter(Brand.identity == identitySchema.identity)
            .first())
        if brand is None:
            raise KeyError(
                f"Brand which has identity {identitySchema.identity} cannot be found")
        return cls.dictionarySerializing([brand])
    
    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Manager)
    @activityLogging(
        category=StaffActivity.Categories.CreatingBrands,
        status=StaffActivity.Statuses.Important)
    def createBrand(cls, creatingSchema: BrandEntireSchema) -> Dict[str, Any]:
        """
            Creating brand with given data received from client.\n
            Returning a dictionary which contains created brand identity and name.
        """
        brand: Brand = Brand()
        try:
            brand.logo = creatingSchema.logo
            brand.name = creatingSchema.name
            brand.countryCode = creatingSchema.countryCode
            brand.website = creatingSchema.website
            brand.socialMediaURL = creatingSchema.socialMediaURL
            brand.phone = creatingSchema.phone
            brand.email = creatingSchema.email
            brand.address = creatingSchema.address
            brand.photos = creatingSchema.photos
            session.add(brand)
            session.commit()
        except SQLAlchemyError as exception:
            session.rollback()
            raise SQLAlchemyError(
                f"Brand name {brand.name} has already existed")
        else:
            return {
                "identity": brand.identity,
                "name": brand.name
            }

    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Manager)
    @activityLogging(
        category=StaffActivity.Categories.UpdatingBrands,
        status=StaffActivity.Statuses.PendingReview)
    def updateBrand(cls, updatingIdentity: int, updatingSchema: BrandPartialSchema) -> Dict[str, int]:
        """
            Updating brand by identity and data retrieved from clients' requests.
            Returning a dictionary of updated brand's identity after updating successfully.
        """
        brand: Optional[Brand] = (
            session.query(Brand)
            .filter(Brand.identity == updatingIdentity)
            .first())
        if brand is not None:
            for field, value in updatingSchema.dict().items():
                if value != UNASSIGNED:
                    setattr(brand, field, value)
            try:
                session.commit()
            except SQLAlchemyError:
                session.rollback()
                raise SQLModelValidationError(
                    f"Cannot update brand which has identity {updatingIdentity}")
            else:
                return {
                    "identity": brand.identity
                }
        else:
            raise KeyError(
                f"Brand which has identity {updatingIdentity} cannot be found")

    @classmethod
    @permissionRequired(minimumPosition=User.Positions.Manager)
    @activityLogging(
        category=StaffActivity.Categories.DeletingBrands,
        status=StaffActivity.Statuses.PendingReview)
    def deleteBrand(cls, deletingIdentity: int) -> Dict[str, int]:
        """
            Deleting brand by identity retrieved from clients.
            Returning a dictionary of brand's identity after deleting successfully.
        """
        brand: Optional[Brand] = (
            session.query(Brand)
            .filter(Brand.identity == deletingIdentity)
            .first())
        if brand is not None:
            session.delete(brand)
            try:
                session.commit()
            except SQLAlchemyError:
                session.rollback()
                raise SQLModelValidationError(
                    f"Cannot delete brand which has identtiy {deletingIdentity}")
            else:
                return {
                    "identity": deletingIdentity
                }
        else:
            raise KeyError(
                f"Brand which has identity {deletingIdentity} cannot be found")
