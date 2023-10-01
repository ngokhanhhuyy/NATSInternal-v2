from app.validation import Validations
from typing import Optional, Union, List, Dict
from pydantic import BaseModel
from app.services.request_validation_service import UNASSIGNED

class ProductEntireSchema(BaseModel):
    name: str
    brandIdentity: int
    categoryIdentity: int
    description: Optional[str]
    unit: str
    publishedPrice: int
    vatFactor: float
    thumbnail: Optional[bytes]
    photos: Optional[List[bytes]]

class ProductPartialSchema(BaseModel):
    name: Optional[str] = UNASSIGNED
    brandIdentity: Optional[int] = UNASSIGNED
    categoryIdentity: Optional[int] = UNASSIGNED
    description: Optional[str] = UNASSIGNED
    unit: Optional[str] = UNASSIGNED
    publishedPrice: Optional[int] = UNASSIGNED
    vatFactor: Optional[float] = UNASSIGNED
    thumbnail: Optional[bytes] = UNASSIGNED
    photos: Optional[List[bytes]] = UNASSIGNED

class ProductRangeSchema(BaseModel):
    startingIdentity: int
    limit: Optional[int]

class ProductIdentitiesSchema(BaseModel):
    identities: List[int]

class ProductIdentitySchema(BaseModel):
    identity: int


