from sqlalchemy import *
from sqlalchemy.orm import *
from app import application
from app.data import getDatabaseSession, Base
from app.models.customer import Customer
from app.models.user import User
from app.models.role import Role
from app.models.order import Order
from app.models.order_item import OrderItem
from app.extensions.date_time import Time
from datetime import datetime, timedelta
from time import time
from dateutil.relativedelta import relativedelta
from random import choice
from faker import Faker
import requests
import uuid
from pydantic import BaseModel, Field, validator, ValidationError, ConfigDict
from abc import ABC as AbstractClass
from abc import abstractclassmethod
from devtools import debug
from typing import List, Sequence, Self, Dict, overload

from app.models.announcement import Announcement
from app.models.role_permission import RolePermission
from app.models.user_permission import UserPermission
from app.models.permission import Permission
from app.models.photo import Photo
from app.models.activity import Activity
from app.models.user_session import UserSession

class ResponseDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    @classmethod
    def fromDatabaseEntity(cls, entity: Base | List[Base]) -> Self:
        ...
    
    @classmethod
    def getTranslatedErrorMessages(cls, exception: ValidationError) -> List[Dict[str, str]]:
        TRANSLATED_ERROR_MESSAGE: Dict[str, Any] = {
            "type_error":   {
                "none": {
                    "not_allowed":  "Giá trị không được để trống."
                }
            },
            "value_error":  {
                "missing":     "[Server Error] Value is missing",
                "number":   {
                    "not_ge": "Giá trị phải lớn hơn hoặc bằng {limit_value}.",
                    "not_le": "Giá trị phải nhỏ hơn bằng bằng {limit_value}."
                }
            }
        }
        translatedMessages: List[Dict[str, str]] = []
        for error in exception.errors():
            errorMessage: str
            errorType: str = error["type"]
            if "." in errorType:
                errorTypeKeys = errorType.split(".")
                translatedMessage: str | dict[str, Any] = TRANSLATED_ERROR_MESSAGE
                for key in errorTypeKeys:
                    if isinstance(translatedMessage, dict) and key in translatedMessage.keys():
                        translatedMessage = translatedMessage[key]
                    else:
                        raise ValueError
                if "ctx" in error.keys():
                    errorMessage = translatedMessage.format(**error.get("ctx"))
                else:
                    errorMessage = translatedMessage
            else:
                errorMessage = error["msg"]
            translatedMessages.append({
                "location":     [location for location in error["loc"]],
                "message":      errorMessage,
            })


class PermissionResponseDTO(ResponseDTO):
    id: int
    name: str
    approvalRequired: bool

class RoleResponseDTO(ResponseDTO):
    id: int
    name: str

class UserProfileResponseDTO(ResponseDTO):
    id: int
    userName: str
    fullName: str
    roles: List[RoleResponseDTO]
    permissions: List[PermissionResponseDTO]

    @classmethod
    def fromDatabaseEntity(cls, user: User) -> Self:
        permissions = []
        for permissionApprovalRequired in user.permissionsWithApprovalRequired:
            permission: Permission = permissionApprovalRequired[0]
            approvalRequired: bool = permissionApprovalRequired[1]
            permissions.append(PermissionResponseDTO(
                id = permission.id,
                name = permission.name,
                approvalRequired = approvalRequired
            ))
        return UserProfileResponseDTO(
            id = user.id,
            userName = user.userName,
            fullName = user.fullName,
            permissions = permissions,
            roles = [role.__dict__ for role in user.roles])
    
with application.app_context():
    session = getDatabaseSession()
    user = session.scalars(
        select(User)
        .options(
            joinedload(User.roles).joinedload(Role.rolePermissions).joinedload(RolePermission.permission),
            joinedload(User.userPermissions).joinedload(UserPermission.permission)
        ).where(User.id == 7)
    ).first()
    try:
        userProfileResponseDTO = UserProfileResponseDTO.fromDatabaseEntity(user)
        debug(userProfileResponseDTO.model_dump())
    except ValidationError as exception:
        debug(exception.errors())

def returningInteger() -> int:
    return "123"

a: bool = returningInteger()

