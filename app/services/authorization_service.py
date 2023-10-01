from sqlalchemy import *
from flask import redirect, url_for, abort, Response
from flask import g as requestContext
from app.errors import AuthorizationError
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.user_permission import UserPermission
from app.models.role_permission import RolePermission
from app.data import getDatabaseSession
from functools import wraps
from typing import Callable

def permissionRequired(permissionName: str) -> Response:
    def decorator(function: Callable[..., Response]) -> Response:
        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any):
            requestedUser: User = requestContext.requestedUser
            session = getDatabaseSession()
            rolePermissionStatement = (
                select(RolePermission.approvalRequired)
                .join(User.roles)
                .join(Role.rolePermissions)
                .join(RolePermission.permission)
                .where(
                    and_(
                        User.id == requestedUser.id,
                        Permission.name == permissionName
                    )
                )
            )
            userPermissionStatement = (
                select(UserPermission.approvalRequired)
                .join(User.userPermissions)
                .join(UserPermission.permission)
                .where(
                    and_(
                        User.id == requestedUser.id,
                        Permission.name == permissionName
                    )
                )
            )
            approvalRequired: bool | None = session.scalars(
                union_all(
                    rolePermissionStatement,
                    userPermissionStatement)
                ).first()
            if approvalRequired is not None:
                if approvalRequired:
                    return "This action needs to be approved by manager before being performed."
                return function(*args, **kwargs)
            abort(404)
        return wrapper
    return decorator