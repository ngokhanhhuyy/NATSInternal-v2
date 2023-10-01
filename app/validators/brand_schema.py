from app.validation import Validations
from typing import Optional, Union, List, Dict
from pydantic import BaseModel, constr, conint, EmailStr, HttpUrl, validator
from datetime import date, datetime
from app.services.request_validation_service import UNASSIGNED

class BrandEntireSchema(BaseModel):
    logo: Optional[bytes]
    name: str
    countryCode: Optional[str]
    website: Optional[HttpUrl]
    socialMediaURL: Optional[HttpUrl]
    phone: Optional[str]
    email: Optional[EmailStr]
    address: Optional[str]
    photos: Optional[List[bytes]]

class BrandPartialSchema(BaseModel):
    logo: Optional[bytes] = UNASSIGNED
    name: Optional[str] = UNASSIGNED
    countryCode: Optional[str] = UNASSIGNED
    website: Optional[HttpUrl] = UNASSIGNED
    socialMediaURL: Optional[HttpUrl] = UNASSIGNED
    phone: Optional[str] = UNASSIGNED
    email: Optional[EmailStr] = UNASSIGNED
    address: Optional[str] = UNASSIGNED
    photos: Optional[List[bytes]] = UNASSIGNED

class BrandRangeSchema(BaseModel):
    startingIdentity: int
    limit: Optional[int]

class BrandIdentitiesSchema(BaseModel):
    identities: list[int]

class BrandIdentitySchema(BaseModel):
    identity: int
