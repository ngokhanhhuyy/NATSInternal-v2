from typing import Optional
from pydantic import BaseModel

class ProductCategorySchema(BaseModel):
    name: str

class ProductCategoryRangeSchema(BaseModel):
    startingIdentity: int
    limit: Optional[int]

class ProductCategoryIdentitiesSchema(BaseModel):
    identities: list[int]

class ProductCategoryIdentitySchema(BaseModel):
    identity: int
    