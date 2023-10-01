from sqlalchemy import *
from flask import request, jsonify, redirect, url_for, Response
from flask import g as requestContext
from app.data import getDatabaseSession
from app.models.user import User
from app.models.activity import Activity
from app.models.permission import Permission
from app.extensions.date_time import Time
from functools import wraps
from typing import List, TYPE_CHECKING

class ActivityService:
    def activityLogging(permissionNames: List[str], objectType: str, objectID: int):
        def decorator(function):
            @wraps
            def wrapper(*args, **kwargs):
                permission: Permission = None
                with getDatabaseSession() as session:
                    permission = session.scalars(
                        select(Permission)
                        .where(Permission.name.in_(permissionNames))
                    ).all()
                user: User = requestContext.user
                activity = Activity()
                activity.userID = user.id
                activity.permission = permission.id
                activity.objectType = objectType

                # Checking if <directly modification> permission is required
                # for this activity to be performed
                if "Chỉnh sửa trực tiếp" in permissionNames :

                # Executing controller login and checking response status code
                response: Response = function(*args, **kwargs)
                if response.status_code == 200:


 
