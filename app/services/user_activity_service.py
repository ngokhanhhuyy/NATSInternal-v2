from flask import request
from flask import g as requestContext
from app.data import session
from app.models.user import User
from app.models.activity import Activity
from functools import wraps

def activityLogging(
        action: Activity.Actions,
        objectType: str | None,
        objectID: int | None):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            actionResult = function(*args, **kwargs)
            requestedStaff: User = requestContext.requestedStaff
            staffActivity = StaffActivity(
                staffIdentity=requestedStaff.identity,
                category=category,
                status=status)
            staffInteractionActivities = [
                StaffActivity.Categories.CreatingStaffs,
                StaffActivity.Categories.ReplacingStaffs,
                StaffActivity.Categories.UpdatingStaffs,
                StaffActivity.Categories.DeletingStaffs
            ]
            if category in staffInteractionActivities:
                text = category.name[0].lower() + category.name[1:] + "Identities"
                staffActivity.newData = {text: actionResult}
            session.add(staffActivity)
            session.commit()
            return actionResult
        return wrapper
    return decorator