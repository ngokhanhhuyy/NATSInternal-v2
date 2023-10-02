from app import application
from flask import g as requestContext
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy.sql import quoted_name
from sqlalchemy import create_engine
from app import application
from app.config import DevelopmentConfig, ProductionConfig
from contextlib import contextmanager
import os
from typing import Type, Generator

# Determine database connection string
if os.getenv("FLASK_ENV") == "development":
    databaseURI = DevelopmentConfig.SQLALCHEMY_DATABASE_URI
elif os.getenv("FLASK_ENV") == "production":
    databaseURI = ProductionConfig.SQLALCHEMY_DATABASE_URI
else:
    raise ValueError("FLASK_ENV variable value is invalid.")
# Create a session
engine = create_engine(
    databaseURI,
    connect_args={"options": "-c timezone=Asia/Ho_Chi_Minh"})
engine.dialect.identifier_preparer._double_percents = True
engine.dialect.identifier_preparer._double_quote = True
engine.dialect.identifier_preparer._quote = lambda value, identifier: quoted_name(value, identifier)
ScopeSession = scoped_session(sessionmaker(
    expire_on_commit=True,
    autocommit=False,
    autoflush=False,
    bind=engine))
Base: DeclarativeMeta = declarative_base()
metadata = Base.metadata

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
    Base.metadata.create_all(bind=engine)

def getDatabaseSession() -> Session:
    if "databaseSession" not in requestContext:
        requestContext.databaseSession = ScopeSession()
    return requestContext.databaseSession

# @application.before_request
# def creatingDatabaseSession():
#     """Creating a new database session for each request."""
#     requestContext.databaseSession: scoped_session[Session] = ScopeSession()

@application.teardown_appcontext
def destroyingDatabaseSession(exception: Exception = None):
    """Destroying existing database session when the request - response circle ended."""
    ScopeSession.close_all()
    engine.dispose()
    print("disposed")

@contextmanager
def getTemporaryDatabaseSession() -> Generator[Session, None, None]:
    session: Session = requestContext.databaseSession
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
