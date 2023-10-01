from flask import g as requestContext
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy.sql import quoted_name
from sqlalchemy import create_engine
from app import application
from app.config import configurations
from contextlib import contextmanager
from typing import Type, Generator

# Determine database path
databaseURI = configurations["databaseURI"]
# Create a session
engine = create_engine(
    databaseURI,
    connect_args={"options": "-c timezone=Asia/Ho_Chi_Minh"})
engine.dialect.identifier_preparer._double_percents = True
engine.dialect.identifier_preparer._double_quote = True
engine.dialect.identifier_preparer._quote = lambda value, identifier: quoted_name(value, identifier)
ScopeSession: Session = scoped_session(sessionmaker(
    expire_on_commit=False,
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
    session: Session = requestContext.databaseSession
    print(id(session))
    return session

@application.before_request
def creatingDatabaseSession():
    """Creating a new database session for each request."""
    requestContext.databaseSession: Session = ScopeSession()

@application.teardown_request
def destroyingDatabaseSession(exception: Exception = None):
    """Destroying existing database session when the request - response circle ended."""
    databaseSession: Session | None = requestContext.pop("databaseSession", None)
    if databaseSession is not None:
        databaseSession.close()

@contextmanager
def getTemporaryDatabaseSession() -> Generator[Session, None, None]:
    session: Session = ScopeSession()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()