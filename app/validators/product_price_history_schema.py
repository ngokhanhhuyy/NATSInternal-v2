from app.validation import Validations
from pydantic import BaseModel
from app.services.request_validation_service import UNASSIGNED
from datetime import datetime
from typing import Optional, Union, List, Dict, Tuple

class ProductPriceHistoryPartialSchema(BaseModel):
    publishedPrice: Optional[int] = UNASSIGNED
    vatFactor: Optional[float] = UNASSIGNED
    changedType: Optional[int] = UNASSIGNED

class ProductPriceHistoryRangeSchema(BaseModel):
    startingIdentity: int
    limit: Optional[int]

class ProductPriceHistoryIdentitiesSchema(BaseModel):
    identities: List[int]

class ProductPriceHistoryIdentitySchema(BaseModel):
    identity: int