from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.exc import IntegrityError
from app.data import getDatabaseSession
from app.models.user import User
from app.services.request_validation_service import UNASSIGNED
from app.extensions.date_time import Time
from app.errors import NotFoundError
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Dict, Any

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
    createdDateTimeDeltaText: str
    updatedDateTime: datetime | None
    updatedDateTimeDeltaText: str
    status: str
    note: str
    profilePicture: UserPhotoResult | None
    secondaryPhotos: List[UserPhotoResult]
    roles: List[UserRoleResult]

class UserService:
    @classmethod
    def getAllUsers(cls) -> Dict[int, Dict[str, Any]]:
        session = getDatabaseSession()
        users = session.scalars(
            select(User)
            .options(
                joinedload(User.roles),
                joinedload(User.photos),
                joinedload(User.session))
            .order_by(User.id)
        ).all()
        return users
    
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
                createdDateTimeDeltaText = Time.getTimeDeltaText(
                    Time.getCurrentDateTime(),
                    user.createdDateTime),
                updatedDateTime = user.updatedDateTime,
                updatedDateTimeDeltaText = Time.getTimeDeltaText(
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
                roles = [UserRoleResult(id = role.id, name = role.name) for role in user.roles])
            return userResult
        else:
            raise NotFoundError(
                modelName="user",
                id=id)