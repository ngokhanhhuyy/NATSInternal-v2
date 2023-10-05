from pydantic import BaseModel, Field, validator, ValidationError
from typing import Tuple, List, Dict, TYPE_CHECKING

class BaseDTO(BaseModel):
    ...
    class Config:
        extra = "ignore"

permissionApprovalRequired: Tuple[bool, str] = [True, 1]
approvalRequired: bool = permissionApprovalRequired[0]
permissionName: str =  permissionApprovalRequired[1]