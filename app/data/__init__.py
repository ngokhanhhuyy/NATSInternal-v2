from app import application
from flask import g as requestContext
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker, Session, DeclarativeBase
from app import application
from app.config import DevelopmentConfig, ProductionConfig
from contextlib import contextmanager
import os
from typing import Type, Generator

# Initializing base class for models
class Base(DeclarativeBase):
    pass

database = SQLAlchemy(application, model_class=Base)

def initializeDatabase():
    from app.models.activity import Activity
    from app.models.activity_request import ActivityRequest
    from app.models.brand import Brand
    from app.models.country import Country
    from app.models.customer import Customer
    from app.models.permission import Permission
    from app.models.product_category import ProductCategory
    from app.models.product_price_history import ProductPriceHistory
    from app.models.product import Product
    from app.models.role import Role
    from app.models.role_permission import RolePermission
    from app.models.user_api_key import UserApiKey
    from app.models.user_session import UserSession
    from app.models.user_permission import UserPermission
    from app.models.user import User
    from app.models.supply import Supply
    from app.models.supply_item import SupplyItem
    from app.models.order import Order
    from app.models.order_item import OrderItem
    from app.models.order_payment import OrderPayment
    from app.models.expense import Expense
    from app.models.expense_category import ExpenseCategory
    from app.models.expense_payee import ExpensePayee
    from app.models.announcement import Announcement
    from app.models.treatment import Treatment
    from app.models.treatment_session import TreatmentSession
    from app.models.treatment_item import TreatmentItem
    from app.models.treatment_payment import TreatmentPayment
    from app.models.photo import Photo

def getDatabaseSession() -> scoped_session[Session]:
    return database.session
