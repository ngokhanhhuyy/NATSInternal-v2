from sqlalchemy import *
from flask import *
from flask import g as requestContext
from app import application
from app.data import getDatabaseSession
from app.models.user import User
from app.models.role import Role
from app.models.photo import Photo
from app.models.announcement import Announcement
from app.extensions.date_time import Time
from typing import Dict

@application.context_processor
def injectingSharedData() -> Dict[str, Any]:
    if request.endpoint != "login":
        data = {}
        # User data
        requestedUser: User = requestContext.requestedUser
        data.update({
            "requestedUser": {
                "id":               requestedUser.id,
                "profilePicture":   requestedUser.profilePicture.contentDecoded if requestedUser.profilePicture is not None else None,
                "userName":         requestedUser.userName,
                "fullName":         requestedUser.fullName,
                "roles":            [role.name for role in requestedUser.roles]
            }
        })
        session = getDatabaseSession()
        # Announcement data
        announcementData = []
        records = session.execute(
            select(User.id, User.fullName, Announcement)
            .join(User.announcements)
            .where(
                and_(
                    Announcement.startingDateTime <= Time.getCurrentDateTime(),
                    Announcement.endingDateTime >= Time.getCurrentDateTime()
                )
            ).order_by(Announcement.startingDateTime)
            .limit(3)
        ).all()
        for record in records:
            userID: int = record[0]
            fullName: str = record[1]
            announcement: Announcement = record[2]
            startingDateTime = Time.addTimeZoneToDateTime(announcement.startingDateTime)
            timeDeltaText = Time.getTimeDeltaText(Time.getCurrentDateTime(), startingDateTime)
            announcementData.append({
                "userID":                   userID,
                "fullName":                 fullName,
                "categoryName":             announcement.category.name,
                "category":                 announcement.category.value,
                "title":                    announcement.title,
                "content":                  announcement.content,
                "timeDelta":                timeDeltaText + " trước"
            })
        data.update({"announcements":       announcementData})
        data.update({"notifications":       []})

        # Breadcrumb data
        breadcrumbData = []
        breadcrumbsNames = {
            "home":                         "Trang chủ",
            "customers":                    "Khách hàng",
            "orders":                       "Đơn hàng",
            "users":                        "Danh sách tài khoản",
            "user":                         "Tài khoản",
            "photos":                       "Danh sách hình ảnh",
            "photo":                        "Hình ảnh",
            "statistics":                   "Thống kê",
            "list":                         "Danh sách",
            "search":                       "Tìm kiếm"
        }
        requestPath = request.path[1:]
        if "home" not in requestPath:
            for item in requestPath.split("/"):
                if not item.isdigit() and not item == "":
                    breadcrumbData.append(breadcrumbsNames[item])
        data.update({"breadcrumb": breadcrumbData})

        # Determining the selected item on menus
        # Check if the current endpoint is requested user's profile
        if request.endpoint == "user" and request.view_args is not None and request.view_args["userID"] == requestedUser.id:
            navigationBarSelectedItem = "profile"
        elif request.endpoint == "home":
            navigationBarSelectedItem = "home"
        else:
            navigationBarSelectedItem = requestPath.split("/")[0]
        data.update({"navigationBarSelected": navigationBarSelectedItem})
        return data
    return {}