from sqlalchemy import *
from sqlalchemy.orm import joinedload, InstrumentedAttribute
from sqlalchemy.exc import NoResultFound
from app.data import getDatabaseSession
from app.models.user import User
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.photo import Photo
from app.models.treatment import Treatment
from app.errors import NotFoundError
from app.extensions.date_time import Time
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, TypedDict
from devtools import debug
from time import time

@dataclass
class CustomerPhotoResult:
    id: int
    content: str

@dataclass
class CustomerInfoResult:
    id: int
    fullName: str
    nickName: str
    company: str
    sex: str
    birthday: date | None
    phone: str
    profilePicture: CustomerPhotoResult | None

@dataclass
class CustomersResult:
    pageCount: int
    customers: List[CustomerInfoResult]

@dataclass
class CustomerIntroducerResult:
    id: int
    fullName: str
    profilePicture: CustomerPhotoResult | None

@dataclass
class CustomerPhotoResult:
    id: int
    content: str

@dataclass
class CustomerPersonalStatisticsResult:
    totalOrderCount: int
    totalOrderAmount: int
    totalTreatmentCount: int
    totalTreatmentAmount: int
    unpaidAmount: int

@dataclass
class CustomerResult:
    id: int
    fullName: str
    nickName: str
    company: str
    sex: str
    birthday: datetime | None
    phone: str
    zalo: str
    facebookURL: str
    email: str
    address: str
    createdTimeDelta: str
    updatedTimeDelta: str
    introducer: CustomerIntroducerResult | None
    note: str
    profilePicture: CustomerPhotoResult | None
    secondaryPhotos: List[CustomerPhotoResult]

@dataclass
class CustomersRankingItemResult:
    id: int
    fullName: str
    sex: str
    profilePicture: str
    value: int

@dataclass
class CustomersRankingResult:
    customers: Dict[int, CustomersRankingItemResult]


class CustomerService:
    @classmethod
    def getAllCustomers(cls, page: int | None, sortByField: str | None, sortOrder: str | None) -> CustomersResult:
        fields = {
            "firstName":        Customer.firstName,
            "lastName":         Customer.lastName,
            "birthday":         Customer.birthday,
            "createdDateTime":  Customer.createdDateTime
        }
        order = asc if sortOrder == "ascending" else desc
        field = fields[sortByField] if sortByField is not None else Customer.firstName
        session = getDatabaseSession()
        # Calculate page count number
        customerCount = session.scalars(
            select(func.count())
            .select_from(Customer)
        ).one()
        # Get all customers
        customers = session.scalars(
            select(Customer)
            .options(joinedload(Customer.photos))
            .order_by(order(field))
            .limit(15)
            .offset((page - 1) * 15 if page is not None else 0)
        ).unique().all()
        customersResult = []
        for customer in customers:
            customersResult.append(CustomerInfoResult(
                id = customer.id,
                fullName = customer.fullName,
                nickName = customer.nickName,
                company = customer.company,
                sex = customer.sex,
                birthday = customer.birthday,
                phone = customer.phone,
                profilePicture = CustomerPhotoResult(
                    id = customer.profilePicture.id,
                    content = customer.profilePicture.contentDecoded
                ) if customer.profilePicture is not None else None
            ))
        result = CustomersResult(
            pageCount = customerCount // 15,
            customers=customersResult
        )
        return result

    @classmethod
    def searchForCustomers(cls, field: str, content: str, page: int | None) -> CustomersResult:
        fields: Dict[str, InstrumentedAttribute[str]] = {
            "fullName":         Customer.fullName,
            "firstName":        Customer.firstName,
            "lastName":         Customer.lastName,
            "phone":            Customer.phone,
        }
        session = getDatabaseSession()
        customerCount = session.scalars(
            select(func.count())
            .select_from(Customer)
            .where(fields[field].ilike(f"%{content}%"))
        ).one()
        customers = session.scalars(
            select(Customer)
            .order_by(Customer.lastName)
            .where(fields[field].ilike(f"%{content}%"))
            .limit(15)
            .offset((page - 1) * 15 if page is not None else 0)
            .options(joinedload(Customer.photos))
        ).unique().all()
        customersResult = []
        for customer in customers:
            customersResult.append(CustomerInfoResult(
                id = customer.id,
                fullName = customer.fullName,
                nickName = customer.nickName,
                company = customer.company,
                sex = customer.sex,
                birthday = customer.birthday,
                phone = customer.phone,
                profilePicture = CustomerPhotoResult(
                    id = customer.profilePicture.id,
                    content = customer.profilePicture.contentDecoded
                ) if customer.profilePicture is not None else None
            ))
        result = CustomersResult(
            pageCount = customerCount // 15,
            customers=customersResult)
        return result

    @classmethod
    def getCustomerByID(cls, customerID: int) -> CustomerResult:
        session = getDatabaseSession()
        customer = session.scalars(
            select(Customer)
            .outerjoin(Customer.photos)
            .where(Customer.id == customerID)
        ).unique().one()
        # Introducer
        introducerResult = None
        if customer.introducer is not None:
            introducerResult = CustomerIntroducerResult(
                id = customer.introducer.id,
                fullName = customer.introducer.fullName,
                profilePicture = CustomerPhotoResult(
                    id = customer.introducer.profilePicture.id,
                    content = customer.introducer.profilePicture.contentDecoded
                ) if customer.introducer.profilePicture is not None else None)
        # Profile picture
        profilePictureResult = None
        if customer.profilePicture is not None:
            profilePictureResult = CustomerPhotoResult(
                id = customer.profilePicture.id,
                content = customer.profilePicture.contentDecoded)
        # Photo
        secondaryPhotosResult = [CustomerPhotoResult(
            id = photo.id,
            content = photo.contentDecoded
        ) for photo in customer.secondaryPhotos]
        # Result
        result = CustomerResult(
            id = customer.id,
            fullName = customer.fullName,
            nickName = customer.nickName,
            company = customer.company,
            sex = customer.sex,
            birthday = customer.birthday,
            phone = customer.phone,
            zalo = customer.zalo,
            facebookURL = customer.facebookURL,
            email = customer.email,
            address = customer.address,
            createdTimeDelta = Time.getTimeDeltaText(
                Time.getCurrentDateTime(),
                customer.createdDateTime),
            updatedTimeDelta = Time.getTimeDeltaText(
                Time.getCurrentDateTime(),
                customer.updatedDateTime),
            introducer = introducerResult,
            note = customer.note,
            profilePicture = profilePictureResult,
            secondaryPhotos = secondaryPhotosResult)
        return result

    @classmethod
    def getCustomerCountsOverLast4Months(cls) -> Dict[str, Dict[str, Any]]:
        session = getDatabaseSession()
        maxRangeDateTime = Time.getCurrentDateTime().strftime('%Y-%m-%d %H:%M:%S')
        minRangeDateTime = (
            Time.getCurrentDateTime() - relativedelta(months=4)
        ).strftime('%Y-%m-%d %H:%M:%S')
        totalCustomerCountQuery = (
            select(
                extract("year", Customer.createdDateTime).label("Year"),
                extract("month", Customer.createdDateTime).label("Month"),
                func.sum(func.count()).over(
                    order_by=(
                        extract("year", Customer.createdDateTime),
                        extract("month", Customer.createdDateTime)
                    )
                ).label("Count")
            ).group_by(column("Year"), column("Month"))
            .alias("TotalCustomerCount")
        )
        MonthYearSeriesQuery = (
            select(
                extract("year", column("series")).label("Year"),
                extract("month", column("series")).label("Month")
            ).select_from(
                func.generate_series(
                    text(f"'{minRangeDateTime}'"),
                    text(f"'{maxRangeDateTime}'"),
                    text("interval '1 month'")
                ).alias("series")
            ).alias("MonthYearSeries")
        )
        rows = session.execute(
            select(
                text('"MonthYearSeries"."Year"'),
                text('"MonthYearSeries"."Month"'),
                func.coalesce(text('"TotalCustomerCount"."Count"'), 0)
            ).select_from(MonthYearSeriesQuery)
            .outerjoin(
                totalCustomerCountQuery,
                and_(
                    text('"MonthYearSeries"."Year" = "TotalCustomerCount"."Year"'),
                    text('"MonthYearSeries"."Month" = "TotalCustomerCount"."Month"')
                )
            ).group_by(
                text('"MonthYearSeries"."Year"'),
                text('"MonthYearSeries"."Month"'),
                text('"TotalCustomerCount"."Count"')
            ).order_by(
                text('"MonthYearSeries"."Year" desc'),
                text('"MonthYearSeries"."Month" desc')
            ).limit(4)
        ).all()
        result = {
            "thisMonth": {
                "name":                 "Tháng này",
                "count":                0
            },    
            "lastMonth": {
                "name":                 None,
                "count":                0
            },   
            "twoMonthsAgo": {
                "name":                 None,
                "count":                0
            }, 
            "threeMonthsAgo": {
                "name":                 None,
                "count":                0
            },
        }
        for i in range(len(rows)):
            month: int = rows[i][1]
            count: int = rows[i][2]
            if i > -1:
                result[list(result.keys())[i]]["name"] = "Tháng " + str(month)
            result[list(result.keys())[i]]["count"] = count
        return result
        
    @classmethod
    def getNewCustomerCountsOverLast4Months(cls) -> Dict[str, Dict[str, Any]]:
        session = getDatabaseSession()
        maxRangeDateTime = Time.getCurrentDateTime().strftime('%Y-%m-%d %H:%M:%S')
        minRangeDateTime = (
            Time.getCurrentDateTime() - relativedelta(months=4)
        ).strftime('%Y-%m-%d %H:%M:%S')
        newCustomerCountQuery = (
            select(
                extract("year", Customer.createdDateTime).label("Year"),
                extract("month", Customer.createdDateTime).label("Month"),
                func.count().label("Count")
            ).group_by(column("Year"), column("Month"))
            .alias("TotalCustomerCount")
        )
        MonthYearSeriesQuery = (
            select(
                extract("year", column("series")).label("Year"),
                extract("month", column("series")).label("Month")
            ).select_from(
                func.generate_series(
                    text(f"'{minRangeDateTime}'"),
                    text(f"'{maxRangeDateTime}'"),
                    text("interval '1 month'")
                ).alias("series")
            ).alias("MonthYearSeries")
        )
        rows = session.execute(
            select(
                text('"MonthYearSeries"."Month"'),
                func.coalesce(text('"TotalCustomerCount"."Count"'), 0)
            ).select_from(MonthYearSeriesQuery)
            .outerjoin(
                newCustomerCountQuery,
                and_(
                    text('"MonthYearSeries"."Year" = "TotalCustomerCount"."Year"'),
                    text('"MonthYearSeries"."Month" = "TotalCustomerCount"."Month"')
                )
            ).group_by(
                text('"MonthYearSeries"."Year"'),
                text('"MonthYearSeries"."Month"'),
                text('"TotalCustomerCount"."Count"')
            ).order_by(
                text('"MonthYearSeries"."Year" desc'),
                text('"MonthYearSeries"."Month" desc')
            ).limit(4)
        ).all()
        result = {
            "thisMonth": {
                "name":                 "Tháng này",
                "count":                0
            },    
            "lastMonth": {
                "name":                 None,
                "count":                0
            },   
            "twoMonthsAgo": {
                "name":                 None,
                "count":                0
            },
            "threeMonthsAgo": {
                "name":                 None,
                "count":                0
            }
        }
        for i in range(len(rows)):
            month = rows[i][0]
            count = rows[i][1]
            if i > 0:
                result[list(result.keys())[i]]["name"] = "Tháng " + str(month)
            result[list(result.keys())[i]]["count"] = count
        return result
        
    @classmethod
    def getLoyalCustomerCountsOverLast4Months(cls) -> Dict[str, Dict[str, Any]]:
        session = getDatabaseSession()
        maxRangeDateTime = Time.getCurrentDateTime().strftime('%Y-%m-%d %H:%M:%S')
        minRangeDateTime = (
            Time.getCurrentDateTime() - relativedelta(months=4)
        ).strftime('%Y-%m-%d %H:%M:%S')
        orderCountSubQuery = (
            select(
                Order.customerID.label("CustomerID"),
                func.count(Order.id).label("Count"),
                extract("year", Order.orderedDateTime).label("Year"),
                extract("month", Order.orderedDateTime).label("Month")
            ).select_from(Order)
            .group_by(column("CustomerID"), column("Year"), column("Month"))
            .having(func.count(Order.id) >= 2)
            .alias("OrderCount")
        )
        monthYearSeriesSubQuery = (
            select(
                extract("year", column("series")).label("Year"),
                extract("month", column("series")).label("Month")
            ).select_from(
                func.generate_series(
                    text(f"'{minRangeDateTime}'"),
                    text(f"'{maxRangeDateTime}'"),
                    text("interval '1 month'")
                ).alias("series")
            ).alias("MonthYearSeries")
        )
        rows = session.execute(
            select(
                text('"MonthYearSeries"."Month"'),
                func.count(text('"OrderCount"."CustomerID"'))
            ).select_from(monthYearSeriesSubQuery)
            .outerjoin(
                orderCountSubQuery,
                and_(
                    text('"MonthYearSeries"."Year" = "OrderCount"."Year"'),
                    text('"MonthYearSeries"."Month" = "OrderCount"."Month"')
                )
            ).group_by(
                text('"MonthYearSeries"."Year"'),
                text('"MonthYearSeries"."Month"')
            ).order_by(
                text('"MonthYearSeries"."Year" desc'),
                text('"MonthYearSeries"."Month" desc')
            ).limit(4)
        ).all()
        result = {
            "thisMonth": {
                "name":                 "Tháng này",
                "count":                0
            },    
            "lastMonth": {
                "name":                 None,
                "count":                0
            },   
            "twoMonthsAgo": {
                "name":                 None,
                "count":                0
            },
            "threeMonthsAgo": {
                "name":                 None,
                "count":                0
            }
        }
        for i in range(len(rows)):
            month = rows[i][0]
            count = rows[i][1]
            if i > 0:
                result[list(result.keys())[i]]["name"] = "Tháng " + str(month)
            result[list(result.keys())[i]]["count"] = count
        return result

    @classmethod
    def getHighValueCustomerCountsOverLast4Months(cls) -> Dict[str, Dict[str, Any]]:
        maxRangeDateTime = (Time.getCurrentDateTime() + relativedelta(months=1)).strftime('%Y-%m-%d %H:%M:%S')
        session = getDatabaseSession()
        maxRangeDateTime = Time.getCurrentDateTime().strftime('%Y-%m-%d %H:%M:%S')
        minRangeDateTime = (
            Time.getCurrentDateTime() - relativedelta(months=4)
        ).strftime('%Y-%m-%d %H:%M:%S')
        orderSubQuery = (
            select(
                Order.customerID.label("customerID"),
                extract("year", Order.orderedDateTime).label("year"),
                extract("month", Order.orderedDateTime).label("month"),
                func.sum(OrderItem.price).label("amount")
            ).select_from(Order)
            .join(Order.items)
            .group_by(Order.customerID, "year", "month")
            .alias("Order")
        )
        qualifiedOrderSubQuery = (
            select(
                column("year").label("year"),
                column("month").label("month"),
                column("customerID").label("customerID"),
                func.sum(text("amount"))
            ).select_from(orderSubQuery)
            .group_by(column("year"), column("month"), column("customerID"))
            .having(func.sum(column("amount")) >= 20000000)
            .alias("QualifiedOrder")
        )
        monthYearSubQuery = (
            select(
                extract("year", column("series")).label("year"),
                extract("month", column("series")).label("month")
            ).select_from(
                func.generate_series(
                    text(f"'{minRangeDateTime}'"),
                    text(f"'{maxRangeDateTime}'"),
                    text("interval '1 month'")
                ).alias("series")
            ).alias("MonthYearSeries")
        )
        rows = session.execute(
            select(
                text('"MonthYearSeries"."month"'),
                func.count(text('"QualifiedOrder"."customerID"'))
            ).select_from(monthYearSubQuery)
            .outerjoin(
                qualifiedOrderSubQuery,
                and_(
                    text('"MonthYearSeries"."year" = "QualifiedOrder"."year"'),
                    text('"MonthYearSeries"."month" = "QualifiedOrder"."month"'),
                )
            ).group_by(
                text('"MonthYearSeries"."year"'),
                text('"MonthYearSeries"."month"')
            ).order_by(
                text('"MonthYearSeries"."year" desc'),
                text('"MonthYearSeries"."month" desc')
            ).limit(4)
        ).all()
        result = {
            "thisMonth": {
                "name":                 "Tháng này",
                "count":                0
            },    
            "lastMonth": {
                "name":                 None,
                "count":                0
            },   
            "twoMonthsAgo": {
                "name":                 None,
                "count":                0
            },
            "threeMonthsAgo": {
                "name":                 None,
                "count":                0
            }
        }
        for i in range(len(rows)):
            month = rows[i][0]
            count = rows[i][1]
            if i > 0:
                result[list(result.keys())[i]]["name"] = "Tháng " + str(month)
            result[list(result.keys())[i]]["count"] = count
        return result

    @classmethod
    def getTop5CustomersByAmountInThisMonth(cls) -> CustomersRankingResult:
        session = getDatabaseSession()
        currentDateTime = Time.getCurrentDateTime()
        rows = session.execute(
            select(
                Customer.id,
                Customer.fullName,
                Customer.sex,
                Photo,
                func.sum(OrderItem.price).label("MonthlyAmount")
            ).select_from(Order)
            .join(OrderItem)
            .join(Order.customer)
            .outerjoin(Customer.photos)
            .where(
                extract("year", Order.orderedDateTime) == currentDateTime.year,
                extract("month", Order.orderedDateTime) == currentDateTime.month,
                or_(Photo.isPrimary == True, Photo.id == None)
            ).group_by(Customer.id, Customer.fullName, Photo.id)
            .order_by(desc("MonthlyAmount"))
            .limit(5)
        ).all()
        customersResult = {}
        for i in range(5):
            if i < len(rows):
                row = rows[i]
                profilePicture: Photo = row[3]
                customersResult.update(
                    {
                        i + 1: CustomersRankingItemResult(
                            id = row[0],
                            fullName = row[1],
                            sex = row[2],
                            profilePicture = profilePicture.contentDecoded if profilePicture is not None else None,
                            value = row[4]
                        )
                    }
                )
        result = CustomersRankingResult(customers = customersResult)
        return result
        
    @classmethod
    def getTop5CustomersByCountInThisMonth(cls) -> CustomersRankingResult:
        session = getDatabaseSession()
        currentDateTime = Time.getCurrentDateTime()
        rows = session.execute(
            select(
                Customer.id,
                Customer.fullName,
                Customer.sex,
                Photo,
                func.count(Order.id).label("OrderCount"),
            ).select_from(Customer)
            .join(Customer.orders)
            .outerjoin(Customer.photos)
            .where(
                extract("year", Order.orderedDateTime) == currentDateTime.year,
                extract("month", Order.orderedDateTime) == currentDateTime.month,
                or_(Photo.isPrimary == True, Photo.id == None)
            ).group_by(Customer.id, Customer.fullName, Photo.id)
            .order_by(desc("OrderCount"), asc(func.max(Order.orderedDateTime)))
            .limit(5)
        ).all()
        customersResult = {}
        for i in range(5):
            if i < len(rows):
                row = rows[i]
                profilePicture: Photo = row[3]
                customersResult.update(
                    {
                        i + 1: CustomersRankingItemResult(
                            id = row[0],
                            fullName = row[1],
                            sex = row[2],
                            profilePicture = profilePicture.contentDecoded if profilePicture is not None else None,
                            value = row[4]
                        )
                    }
                )
        result = CustomersRankingResult(customers = customersResult)
        return result
        
    @classmethod
    def getNewCustomerDeltaTimeOverLast6Months(cls) -> Dict[str, float]:
        session = getDatabaseSession()
        maxRangeDateTime = Time.getCurrentDateTime().strftime('%Y-%m-%d %H:%M:%S')
        customerDeltaQuery = (
            select(
                Customer.createdDateTime.label("CreatedDateTime"),
                func.lag(Customer.createdDateTime)
                    .over(order_by=Customer.createdDateTime).label("PreviousDateTime"),
                extract("year", Customer.createdDateTime).label("Year"),
                extract("month", Customer.createdDateTime).label("Month")
            )
        ).alias("CustomerDelta")
        monthSeriesSubQuery = (
            select(
                extract("year", column("series")).label("Year"),
                extract("month", column("series")).label("Month")
            ).select_from(
                func.generate_series(
                    select(func.min(Customer.createdDateTime)).scalar_subquery(),
                    text(f"'{maxRangeDateTime}'"),
                    text("interval '1 month'")
                ).alias("series")
            ).alias("MonthYearSeries")
        ).alias("MonthSeries")
        rows = session.execute(
            select(
                text('"MonthSeries"."Year"'),
                text('"MonthSeries"."Month"'),
                func.avg(
                    text('"CustomerDelta"."CreatedDateTime" - "CustomerDelta"."PreviousDateTime"'))
                    .label("AverageDelta")
            ).select_from(customerDeltaQuery)
            .outerjoin(
                monthSeriesSubQuery,
                and_(
                    text('"CustomerDelta"."Year" = "MonthSeries"."Year"'),
                    text('"CustomerDelta"."Month" = "MonthSeries"."Month"')
                )
            ).group_by(
                text('"MonthSeries"."Year"'), 
                text('"MonthSeries"."Month"')
            ).order_by(
                text('"MonthSeries"."Year" desc'),
                text('"MonthSeries"."Month" desc')
            ).limit(6)
        ).all()
        data = {}
        for i in reversed(range(len(rows))):
            row: tuple[int, int, timedelta] = rows[i]
            _year, month, delta = row
            if i == 0:
                data["Tháng này"] = round(delta.total_seconds() / (24 * 60 * 60), 2)
            else:
                data[f"Tháng {month}"] = round(delta.total_seconds() / (24 * 60 * 60), 2)
        return data