from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.exc import IntegrityError
from app.data import getDatabaseSession
from app.models.user import User
from app.services.request_validation_service import UNASSIGNED
from app.errors import NotFoundError
from typing import List, Dict, Any

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
        return cls.dictionarySerializing(users)

    # @classmethod
    # def getStaffsByIdentities(cls, identitiesSchema: StaffIdentitiesSchema) -> Dict[int, Dict[str, Any]]:
    #     """
    #         Getting staffs data as a dictionary ordered by identity ascendingly in given identity list.\n
    #         Each element contains <key> as identity of staff and <value> as a dictionary which contains
    #         other fields of the staff.\n
    #         gettingStaffsByIdentity(identities = [1, 2, 3, 4, 5])\n
    #         => Returning staffs which identities are [1, 2, 3, 4, 5].
    #     """
    #     requestedStaff: User = requestContext.requestedStaff
    #     identities = identitiesSchema.identities
    #     staffs: List[User] = (
    #         session.query(User)
    #         .filter(
    #             and_(
    #                 User.position <= requestedStaff.position,
    #                 User.identity.in_(identities)
    #             )
    #         )
    #         .order_by(User.identity)
    #         .all())
    #     for identity in identities:
    #         if identity not in [staff.identity for staff in staffs]:
    #             raise KeyError(f"Staff who has identity {identity} cannot be found")
    #     return cls.serialize(staffs=staffs)

    # @classmethod
    # def getStaffsInRange(cls, rangeSchema: StaffRangeSchema) -> Dict[int, Dict[str, Any]]:
    #     """
    #         Getting staffs data as a dictionary ordered by identity ascendingly in given range.\n
    #         Each element contains <key> as identity and <value> as a dictionary which contains
    #         other fields of the staff.\n
    #         getStaffsByRange(statingIdentity = 1, limit = 5)\n
    #         => Returning staffs which identities are [1, 2, 3, 4, 5].
    #     """
    #     requestedStaff: User = requestContext.requestedStaff
    #     staffs = ( 
    #         session.query(User)
    #         .filter(
    #             and_(
    #                 User.identity >= rangeSchema.startingIdentity,
    #                 User.position <= requestedStaff.position))
    #         .order_by(User.identity)
    #         .limit(rangeSchema.limit)
    #         .all())
    #     return cls.serialize(staffs=staffs)
    
    @classmethod
    def getUserByID(cls, id: int) -> Dict[int, Dict[str, Any]]:
        session = getDatabaseSession()
        user = session.scalars(
            select(User)
            .options(
                joinedload(User.roles),
                joinedload(User.photos),
                joinedload(User.session))
            .where(User.id == id)
        ).first()
        if user is None:
            raise NotFoundError(
                modelName="user",
                id=id)
        return cls.dictionarySerializing(users=[user])

    # @classmethod
    # def createStaff(cls, creatingSchema: StaffEntireSchema) -> Dict[str, Any]:
    #     """
    #         Creating staff with given data received from client.\n
    #         Returning a dictionary which contains created staff identity and username.
    #     """
    #     try:
    #         staff: User = User()
    #         staff.profilePicture = creatingSchema.profilePicture
    #         staff.userName = creatingSchema.userName
    #         staff.password = creatingSchema.password
    #         staff.fullName = creatingSchema.fullName
    #         staff.nickName = creatingSchema.nickName
    #         staff.sex = creatingSchema.sex
    #         staff.birthday = creatingSchema.birthday
    #         staff.phone = creatingSchema.phone
    #         staff.email = creatingSchema.email
    #         staff.zalo = creatingSchema.zalo
    #         staff.facebookURL = creatingSchema.facebookURL
    #         staff.idCardNumber = creatingSchema.idCardNumber
    #         staff.joiningDate = creatingSchema.joiningDate
    #         staff.position = creatingSchema.position
    #         staff.status = creatingSchema.status
    #         staff.note = creatingSchema.note
    #         session.add(staff)
    #         session.commit()
    #     except Exception as exception:
    #         session.rollback()
    #         raise exception
    #     else:
    #         return {
    #             "identity": staff.identity,
    #             "userName": staff.userName
    #         }

    # @classmethod
    # def updateStaff(cls, updatingIdentity: int, updatingSchema: StaffPartialSchema) -> Dict[str, int]:
    #     """
    #         Updating staff by identity and data retrieved from clients' requests.
    #         Returning a dictionary of updated staff's identity and userName after updateing successfully.
    #     """
    #     requestedStaff: User = requestContext.requestedStaff
    #     managerPositions = [
    #         User.Positions.Manager,
    #         User.Positions.Director,
    #     ]
    #     adminPositions = [
    #         User.Positions.Owner,
    #         User.Positions.Developer
    #     ]
    #     isManager: bool = requestedStaff.position in [position.value for position in managerPositions]
    #     isAdmin: bool = requestedStaff.position in [position.value for position in adminPositions]
    #     staff: User = (
    #         session.query(User)
    #         .filter(User.identity == updatingIdentity)
    #         .first())
    #     if staff is not None:
    #         hasHigherPosition = requestedStaff.position > staff.position
    #         isThisFamilyMember = staff.position == User.Positions.FamilyMember.value
    #         if not (isAdmin or (hasHigherPosition and isManager and not isThisFamilyMember)):
    #             raise PermissionError(
    #                 "You don't have permission to update this staff account")
    #         for field, value in updatingSchema.dict().items():
    #             if value != UNASSIGNED:
    #                 setattr(staff, field, value)
    #         try:
    #             session.commit()
    #         except IntegrityError:
    #             session.rollback()
    #             raise SQLModelValidationError(
    #                 f"Username '{updatingSchema.userName}' is already existing")
    #     else:
    #         raise KeyError
    #     return {
    #         "identity": staff.identity,
    #         "userName": staff.userName
    #     }

    # @classmethod
    # def deleteStaff(cls, deletingIdentity: int) -> Dict[str, Any]:
    #     """
    #         Deleting staff by identity retrieved from clients.
    #         Returning a dictionary of staff's identity and username after deleting successfully.
    #     """
    #     requestedStaff: User = requestContext.requestedStaff
    #     managerPositions = [
    #         User.Positions.Manager,
    #         User.Positions.Director,
    #     ]
    #     adminPositions = [
    #         User.Positions.Owner,
    #         User.Positions.Developer
    #     ]
    #     isManager: bool = requestedStaff.position in [position.value for position in managerPositions]
    #     isAdmin: bool = requestedStaff.position in [position.value for position in adminPositions]
    #     staff: User = (
    #         session.query(User)
    #         .filter(User.identity == deletingIdentity)
    #         .first())
    #     if staff is not None:
    #         hasHigherPosition = requestedStaff.position > staff.position
    #         isThisFamilyMember = staff.position == User.Positions.FamilyMember.value
    #         if not (isAdmin or (hasHigherPosition and isManager and not isThisFamilyMember)):
    #             raise PermissionError(
    #                 "You don't have permission to edit this staff account")
    #         session.delete(staff)
    #         return {
    #             "identity": staff.identity,
    #             "userName": staff.userName
    #         }
    #     else:
    #         raise KeyError(
    #             "Staff account which identity is '{deletingIdentity}' "
    #             "cannot be found")