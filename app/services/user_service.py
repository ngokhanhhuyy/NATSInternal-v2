from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.data import getDatabaseSession
from app.models.user import User
from app.services.request_validation_service import UNASSIGNED
from app.extensions.date_time import Time
from app.errors import NotFoundError
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Dict, Any
from devtools import debug

@dataclass
class UserPhotoResult:
    id: int
    content: str

@dataclass
class UserRoleResult:
    id: int
    name: str

@dataclass
class UserProfileResult:
    id: int
    userName: str
    fullName: str
    sex: str
    birthday: date | None
    phone: str
    email: str
    idCardNumber: str
    joiningDate: date | None
    createdDateTime: datetime | None
    createdTimeDeltaText: str
    updatedDateTime: datetime | None
    updatedTimeDeltaText: str
    status: str
    note: str
    profilePicture: UserPhotoResult | None
    secondaryPhotos: List[UserPhotoResult]
    roles: List[UserRoleResult]
    onlineStatus: str 

class UserService:
    @classmethod
    def getAllUsers(cls) -> List[Dict[str, Any]]:
        session = getDatabaseSession()
        users = session.scalars(
            select(User)
            .options(
                joinedload(User.roles),
                joinedload(User.photos),
                joinedload(User.session))
            .order_by(User.id)
        ).all()
        return [user.__dict__ for user in users]
    
    @classmethod
    def getUserByID(cls, id: int) -> UserProfileResult:
        session = getDatabaseSession()
        user = session.scalars(
            select(User)
            .options(
                joinedload(User.roles),
                joinedload(User.photos),
                joinedload(User.session))
            .where(User.id == id)
        ).first()
        if user is not None:
            if user.isOnline:
                onlineStatus = "Online"
            elif user.session is not None:
                onlineStatus = Time.getTimeDeltaText(
                    Time.getCurrentDateTime(),
                    user.session.lastAccessDateTime)
            else:
                onlineStatus = "Offline"
            userResult = UserProfileResult(
                id = user.id,
                userName = user.userName,
                fullName = user.fullName,
                sex = user.sex,
                birthday = user.birthday,
                phone = user.phone,
                email = user.email,
                idCardNumber = user.idCardNumber,
                joiningDate = user.joiningDate,
                createdDateTime = user.createdDateTime,
                createdTimeDeltaText = Time.getTimeDeltaText(
                    Time.getCurrentDateTime(),
                    user.createdDateTime),
                updatedDateTime = user.updatedDateTime,
                updatedTimeDeltaText = Time.getTimeDeltaText(
                    Time.getCurrentDateTime(),
                    user.updatedDateTime),
                status = user.status,
                note = user.note,
                profilePicture = UserPhotoResult(
                    id = user.profilePicture.id,
                    content = user.profilePicture.contentDecoded
                ) if user.profilePicture is not None else None,
                secondaryPhotos = [UserPhotoResult(
                    id = photo.id,
                    content = photo.contentDecoded) for photo in user.secondaryPhotos],
                roles = [UserRoleResult(id = role.id, name = role.name) for role in user.roles],
                onlineStatus = user.onlineStatus)
            debug(userResult)
            return userResult
        else:
            raise NotFoundError(
                modelName="user",
                id=id)