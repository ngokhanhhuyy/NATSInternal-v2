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
            rolePermissionObject: RolePermission = None
            for role in requestedUser.roles:
                for rolePermission in role.rolePermissions:
                    if rolePermission.permission.name == permissionName:
                        rolePermissionObject = rolePermission
                        break
            if rolePermissionObject is not None:
                if rolePermissionObject.approvalRequired:
                    return "This action needs to be approved by manager before being performed."
                return function(*args, **kwargs)
            userPermissionObject: UserPermission = None
            for userPermission in requestedUser.userPermissions:
                if userPermission.permission.name == permissionName:
                    userPermissionObject = userPermission
                    break
            if userPermissionObject is not None:
                if userPermissionObject.approvalRequired:
                    return "This action needs to be approved by manager before being performed."
                return function(*args, **kwargs)
            abort(403)
        return wrapper
    return decorator