from sqlalchemy import *
from sqlalchemy.orm import *
from app.data import getDatabaseSession, getTemporaryDatabaseSession
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
from devtools import debug

from app.models.announcement import Announcement
from app.models.role_permission import RolePermission
from app.models.user_permission import UserPermission
from app.models.permission import Permission
from app.models.photo import Photo
from app.models.activity import Activity
from app.models.user_session import UserSession

with getTemporaryDatabaseSession() as session:
    user = session.execute(
        select(User)
        .join(User.session)
    ).first()