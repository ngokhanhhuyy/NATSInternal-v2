from app.validation import Validations
from typing import Optional, Union, List, Dict
from pydantic import BaseModel, constr, conint, EmailStr, HttpUrl, validator
from datetime import date, datetime
from app.services.request_validation_service import UNASSIGNED

class StaffEntireSchema(BaseModel):
    profilePicture: bytes = None
    userName: str
    password: str
    fullName: str
    nickName: Union[str, None]
    sex: int
    birthday: Union[date, None]
    phone: Union[str, None]
    email: Union[EmailStr, None]
    zalo: Union[str, None]
    facebookURL: Union[HttpUrl, None]
    idCardNumber: Union[str, None]
    joiningDate: Union[date, None]
    position: int
    status: int
    note: Union[str, None]

class StaffPartialSchema(BaseModel):
    profilePicture: Union[bytes, None] = UNASSIGNED
    userName: str = UNASSIGNED
    password: str = UNASSIGNED
    fullName: str = UNASSIGNED
    nickName: Union[str, None] = UNASSIGNED
    sex: int = UNASSIGNED
    birthday: Union[date, None] = UNASSIGNED
    phone: Union[str, None] = UNASSIGNED
    email: Union[EmailStr, None] = UNASSIGNED
    zalo: Union[str, None] = UNASSIGNED
    facebookURL: Union[HttpUrl, None] = UNASSIGNED
    idCardNumber: Union[str, None] = UNASSIGNED
    joiningDate: Union[date, None] = UNASSIGNED
    position: int = UNASSIGNED
    status: int = UNASSIGNED
    note: Union[str, None] = UNASSIGNED

class StaffRangeSchema(BaseModel):
    startingIdentity: int
    limit: Union[int, None]

class StaffIdentitiesSchema(BaseModel):
    identities: List[int]

class StaffIdentitySchema(BaseModel):
    identity: int

