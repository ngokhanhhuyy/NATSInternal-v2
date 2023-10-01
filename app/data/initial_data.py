from sqlalchemy import *
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.exc import IntegrityError
from app import bcrypt
from app.data import getDatabaseSession
from app.models.customer import Customer
from app.models.user import User
from app.models.user_permission import UserPermission
from app.models.brand import Brand
from app.models.country import Country
from app.models.product import Product
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.product_category import ProductCategory
from app.models.permission import Permission
from app.models.supply import Supply
from app.models.supply_item import SupplyItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_payment import OrderPayment
from app.models.expense import Expense
from app.models.expense_category import ExpenseCategory
from app.models.expense_payee import ExpensePayee
from app.models.announcement import Announcement
from app.models.photo import Photo
from app.enum import Sexes
from app.extensions.date_time import Time
import sqlite3
from faker import Faker
from random import choice, randrange, uniform
from vn_fullname_generator import generator
import secrets
import requests
import cairosvg
from PIL import Image
import uuid
from io import BytesIO
from datetime import date, datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from typing import List, Dict, TypedDict

connection = sqlite3.connect("app/data/database.db")
cursor = connection.cursor()
cursor.row_factory = sqlite3.Row

openingDateTime = Time.getCurrentDateTime() - timedelta(days=365 * 5)
openingUserCount = 8
preparingDateTime = openingDateTime - timedelta(days=7)

def initializeData():
    # Preparing data which isn't related to the business performance
    initializeCountry()
    initializeProductCategory()
    initializeRole()
    initializeUser()
    initializeUserApiKey()
    initializeUserRole()
    initializePermission()
    initializeRolePermission()
    initializeBrand()
    initializeProduct()
    # Initializing business data which is created using business growth simulation
    initializeCustomer()
    initializeSupplyAndSupplyItem()
    initializeOrderAndOrderItem()
    initializeOrderPayment()
    initializeExpenseCategory()
    initializeExpensePayee()
    initializeExpense()
    initializeAnnouncement()
    initializePhoto()
    pass

def initializeCountry():
    with getDatabaseSession() as session:
        if session.query(Country).count() == 0:
            with open("app/data/country_codes.txt", "r", encoding="utf-8") as file:
                lines = file.readlines()
                for line in lines:
                    fields = line.split("  ")
                    code = fields[0]
                    name = fields[1].replace("\n", "")
                    assert len(name) <= 40
                    country = Country()
                    country.name = name
                    country.code = code
                    session.add(country)
                    print(f"Created country <{name}>")
            session.commit()

def initializeBrand():
    with getDatabaseSession() as session:
        if session.query(Brand).count() == 0:
            brandsData = [
                {
                    "name":                 "Samsung",
                    "country":              "Hàn Quốc",
                    "website":              "https:www.samsung.com",
                },
                {
                    "name":                 "Apple Inc",
                    "country":              "Hoa Kỳ",
                    "website":              "apple.com",
                },
                {
                    "name":                 "HTC Corporation",
                    "country":              "Đài Loan",
                    "website":              "htc.com"
                }
            ]
            countries = session.scalars(
                select(Country)
            ).all()
            for brandData in brandsData:
                brand = Brand()
                brand.name = brandData["name"]
                brand.countryID = next(country.id for country in countries if country.name == brandData["country"])
                brand.website = brandData["website"]
                brand.socialMediaURL = ""
                brand.phone = ""
                brand.email = ""
                brand.address = ""
                session.add(brand)
                print(f"Created brand <{brand.name}>")
            session.commit()

def initializeProduct():
    with getDatabaseSession() as session:
        if session.query(Product).count() == 0:
            productsData = {
                "Samsung": [
                    {
                        "name":             "Galaxy S9",
                        "price":            5_000_000,
                    },
                    {
                        "name":             "Galaxy S10",
                        "price":            7_000_000,
                    },
                    {
                        "name":             "Galaxy S20",
                        "price":            9_000_000,
                    },
                    {
                        "name":             "Galaxy S20+",
                        "price":            10_000_000,
                    },
                    {
                        "name":             "Galaxy S21",
                        "price":            12_000_000,
                    },
                    {
                        "name":             "Galaxy S21+",
                        "price":            13_000_000,
                    },
                    {
                        "name":             "Galaxy S22",
                        "price":            15_000_000,
                    },
                    {
                        "name":             "Galaxy S22+",
                        "price":            16_000_000,
                    },
                    {
                        "name":             "Galaxy S23",
                        "price":            20_000_000,
                    },
                    {
                        "name":             "Galaxy S23+",
                        "price":            21_000_000,
                    },
                ],
                "Apple Inc": [
                    {
                        "name":             "iPhone 7",
                        "price":            3_000_000,
                    },
                    {
                        "name":             "iPhone 7 Plus",
                        "price":            3_500_000,
                    },
                    {
                        "name":             "iPhone 8",
                        "price":            4_500_000,
                    },
                    {
                        "name":             "iPhone 8 Plus",
                        "price":            5_000_000,
                    },
                    {
                        "name":             "iPhone X",
                        "price":            6_000_000,
                    },
                    {
                        "name":             "iPhone XS",
                        "price":            7_500_000,
                    },
                    {
                        "name":             "iPhone XS Max",
                        "price":            8_000_000,
                    },
                    {
                        "name":             "iPhone 11",
                        "price":            8_500_000,
                    },
                    {
                        "name":             "iPhone 11 Pro",
                        "price":            9_000_000,
                    },
                    {
                        "name":             "iPhone 11 Pro Max",
                        "price":            9_000_000,
                    },
                    {
                        "name":             "iPhone 12 Mini",
                        "price":            9_000_000,
                    },
                    {
                        "name":             "iPhone 12",
                        "price":            9_500_000,
                    },
                    {
                        "name":             "iPhone 12 Pro",
                        "price":            10_000_000,
                    },
                    {
                        "name":             "iPhone 12 Pro Max",
                        "price":            12_000_000,
                    },
                    {
                        "name":             "iPhone 13 Mini",
                        "price":            12_500_000,
                    },
                    {
                        "name":             "iPhone 13",
                        "price":            14_000_000,
                    },
                    {
                        "name":             "iPhone 13 Pro",
                        "price":            15_000_000,
                    },
                    {
                        "name":             "iPhone 13 Pro Max",
                        "price":            16_500_000,
                    },
                    {
                        "name":             "iPhone 14 Mini",
                        "price":            16_000_000,
                    },
                    {
                        "name":             "iPhone 14",
                        "price":            17_000_000,
                    },
                    {
                        "name":             "iPhone 14 Pro",
                        "price":            19_000_000,
                    },
                    {
                        "name":             "iPhone 14 Pro Max",
                        "price":            21_500_000,
                    },
                ],
                "HTC Corporation": [
                    {
                        "name":             "One X",
                        "price":            500_000,
                    },
                    {
                        "name":             "One M7",
                        "price":            600_000,
                    },
                    {
                        "name":             "One M8",
                        "price":            900_000,
                    },
                    {
                        "name":             "One M9",
                        "price":            1_200_000,
                    },
                ]
            }
            brands = session.scalars(
                select(Brand)
            ).all()
            categories = session.scalars(
                select(ProductCategory)
            ).all()
            for brandName, brandProducts in productsData.items():
                for productData in brandProducts:
                    product = Product()
                    product.name = productData["name"]
                    product.brandID = next((brand.id for brand in brands if brand.name == brandName), None)
                    product.categoryID = next((category.id for category in categories if category.name == "Điện thoại"), None)
                    product.description = ""
                    product.unit = "cái"
                    product.price = productData["price"]
                    product.vatFactor = 0.1
                    product.createdDateTime = preparingDateTime
                    session.add(product)
                    print(f"Created product <{product.name}>")
            session.commit()

def initializeProductCategory():
    with getDatabaseSession() as session:
        if session.query(ProductCategory).count() == 0:
            # initialProductCategoryNames = [
            #     "Không xác định",
            #     "Thực phẩm chức năng",
            #     "Sản phẩm dinh dưỡng",
            #     "Thuốc bôi",
            #     "Thuốc uống",
            #     "Thuốc đắp",
            #     "Thuốc xịt"
            # ]
            # for name in initialProductCategoryNames:
            #     productCategory = ProductCategory()
            #     productCategory.name = "Điện thoại"
            #     productCategory.isDefault = name
            #     session.add(productCategory)
            category = ProductCategory()
            category.name = "Điện thoại"
            category.createdDateTime = preparingDateTime
            session.add(category)
            session.commit()

def initializeCustomer(): 
    with getDatabaseSession() as session:
        if session.query(Customer).count() == 0:
            currentDateTime = openingDateTime
            lastCheckedDateTime = openingDateTime
            createdCustomerCount = 0
            daysTakenPerNewCustomer = 15.0
            growthRatePer30Days = 1.018
            while currentDateTime <= Time.getCurrentDateTime():
                fakerGen = Faker()
                jpFakerGen = Faker("ja_JP")
                profile = fakerGen.profile()
                sex = choice([Sexes.Male, Sexes.Female])
                fullName = generator.generate(1 if sex == Sexes.Male else 0)
                nameSegments = fullName.split(" ")
                customer = Customer()
                customer.firstName = nameSegments[0]
                customer.middleName = " ".join(nameSegments[1:len(nameSegments) - 1])
                customer.lastName = nameSegments[len(nameSegments) - 1]
                customer.nickName = profile["name"].split(" ")[0]
                customer.company = profile["company"]
                customer.sex = Sexes.Male if profile["sex"] == "M" else Sexes.Female
                customer.birthday = profile["birthdate"] .strftime("%Y-%m-%d")
                customer.phone = jpFakerGen.phone_number().replace("+", "").replace("-", "")
                customer.zalo = jpFakerGen.phone_number().replace("+", "").replace("-", "")
                customer.facebookURL = "https://facebook.com/" + profile["username"]
                customer.email = profile["mail"]
                customer.address = profile["residence"]
                customer.note = ""
                customer.createdDateTime = currentDateTime
                customer.updatedDateTime = currentDateTime
                session.add(customer)
                session.flush()
                print(f"Created customer: id {customer.id}")
                # Adjusting chance figure
                currentDateTime += timedelta(
                    days=uniform(
                        min(0, daysTakenPerNewCustomer - 1.5),
                        daysTakenPerNewCustomer + 1.5))
                if (currentDateTime - lastCheckedDateTime).days >= timedelta(days=30).days:
                    lastCheckedDateTime += timedelta(days=30)
                    daysTakenPerNewCustomer /= growthRatePer30Days
                createdCustomerCount += 1
            session.commit()

def initializeRole():
    with getDatabaseSession() as session:
        statement = select(func.count()).select_from(Role)
        rowCount: int = session.scalars(statement).one()
        if rowCount == 0:
            roleNames = [
                "Cộng tác viên",
                "Nhân viên",
                "Kế toán",
                "Thu ngân",
                "Quản lý",
                "Giám đốc",
                "Thành viên gia đình",
                "Nhà phát triển"
            ]
            for name in roleNames:
                role = Role()
                role.name = name
                session.add(role)
            session.commit()
        
def initializeUser():
    fakerGen = Faker()
    jpFakerGen = Faker("ja_JP")
    vnFakerGen = Faker("")
    with getDatabaseSession() as session:
        if session.query(User).count() == 0:
            # Adding developer user account 1
            myUser1 = User()
            myUser1.userName = "ngokhanhhuyy"
            myUser1.password = "Huyy47b1"
            myUser1.firstName = "Ngô"
            myUser1.middleName = "Khánh"
            myUser1.lastName = "Huy"
            myUser1.sex = Sexes.Male
            myUser1.birthday = date(year=1997, month=8, day=30),
            myUser1.phone = "09037632117"
            myUser1.email = "ngokhanhhuyy@gmail.com"
            myUser1.idCardNumber = "1234566789"
            myUser1.joiningDate = openingDateTime
            myUser1.status = User.Statuses.Active
            myUser1.note = ""
            session.add(myUser1)
            session.flush()
            print(f"Created user: id {myUser1.id}")
            # Adding developer user account 2
            myUser2 = User()
            myUser2.userName = "quocnv3"
            myUser2.password = "123456789"
            myUser2.firstName = "Nguyễn"
            myUser2.middleName = "Văn"
            myUser2.lastName = "Quốc"
            myUser2.sex = Sexes.Male
            myUser2.birthday = date(year=1997, month=8, day=30),
            myUser2.phone = "09037632117"
            myUser2.email = "quocnv1@gmail.com"
            myUser2.idCardNumber = "1234566789"
            myUser2.joiningDate = openingDateTime
            myUser2.status = User.Statuses.Active
            myUser2.note = ""
            session.add(myUser2)
            session.flush()
            print(f"Created user: id {myUser2.id}")
            # Creating random user accounts
            roleNames = session.scalars(
                select(Role.name)
                .where(Role.name != "Nhà phát triển")
            ).all()
            for i in range(len(roleNames) + 3):
                while True:
                    profile: Dict[str, Any] = fakerGen.profile()
                    phone: str = str(jpFakerGen.phone_number()).replace("-", "").replace("(", "").replace(")", "")
                    sex = choice([Sexes.Male, Sexes.Female])
                    fullName = generator.generate(1 if sex == Sexes.Male else 0)
                    nameSegments = fullName.split(" ")
                    user = User()
                    user.userName = profile["username"]
                    user.passwordHash = bcrypt.generate_password_hash(secrets.token_hex(4)).decode("utf-8")
                    user.firstName = nameSegments[0]
                    user.middleName = " ".join(nameSegments[1:len(nameSegments) - 1])
                    user.lastName = nameSegments[len(nameSegments) - 1]
                    user.sex = sex
                    user.birthday = profile["birthdate"]
                    user.phone = phone
                    user.email = profile["mail"]
                    user.idCardNumber = str(profile["ssn"]).replace("-", "")
                    user.joiningDate = openingDateTime - timedelta(days=randrange(1, 4))
                    user.status = choice([status for status in User.Statuses])
                    if i < len(roleNames) and roleNames[i] in ["Giám đốc", "Thành viên gia đình", "Quản lý"]:
                        user.createdDateTime = openingDateTime
                    else:
                        user.createdDateTime = openingDateTime + timedelta(hours=randrange(12, 72, 12))
                    user.updatedDateTime = openingDateTime
                    user.note = ""
                    session.add(user)
                    try:
                        session.flush()
                        break
                    except IntegrityError:
                        session.rollback()
                print(f"Created user: id {user.id + 1}")
            session.commit()

def initializeUserApiKey():
    from app.models.user_api_key import UserApiKey
    with getDatabaseSession() as session:
        if session.query(UserApiKey).count() == 0:
            statement = select(User.id, User.createdDateTime).order_by(User.id)
            rows: List[Sequence[int, datetime]] = session.execute(statement).all()
            for row in rows:
                userID: int = row[0]
                userCreatedDateTime: datetime = row[1]
                userApiKey = UserApiKey(userID=userID)
                userApiKey.createdDateTime = userCreatedDateTime
                session.add(userApiKey)
                print(f"Created user API key: userID {userID}, API Key {userApiKey.key}")
            session.commit()

def initializeUserRole():
    with getDatabaseSession() as session:
        rowCount = session.scalars(
            select(func.count())
            .select_from(User)
            .join(User.roles)
        ).one()
        if rowCount == 0:
            users = session.scalars(
                select(User)
                .order_by(User.id)
            ).all()
            rolesOnOneRoleUsers = session.scalars(
                select(Role)
                .order_by(Role.id.desc())
                .where(Role.name != "Nhà phát triển")
            ).all()
            twoRolesList = [
                ["Kế toán", "Thu ngân"],
                ["Thu ngân", "Nhân viên"],
                ["Kế toán", "Nhân viên"]
            ]
            twoRolesIndex = 0
            oneRoleIndex = 0
            for i in range(len(users)):
                user = users[i]
                # Developers
                if i < 2:
                    developerRole = session.scalars(
                        select(Role)
                        .where(Role.name == "Nhà phát triển")
                    ).one()
                    user.roles.append(developerRole)
                    print(f"Assigned role <{developerRole.name}> for user {user.id} {user.userName}")
                # Users who have 1 role
                elif i < len(users) - 3:
                    role = rolesOnOneRoleUsers[oneRoleIndex]
                    user.roles.append(role)
                    print(f"Assigned role <{role.name}> for user {user.id} {user.userName}")
                    oneRoleIndex += 1
                else:
                    roles = session.scalars(
                        select(Role)
                        .where(Role.name.in_(twoRolesList[twoRolesIndex]))
                    ).all()
                    for role in roles:
                        user.roles.append(role)
                        print(f"Assigned role <{role.name}> for user {user.id} {user.userName}")
                    twoRolesIndex += 1
                session.flush()
            session.commit()

def initializePermission():
    with getDatabaseSession() as session:
        rowCount = session.scalars(select(func.count()).select_from(Permission)).one()
        if rowCount == 0:
            permissionNames = [
                "Tạo tài khoản",
                "Xem tài khoản",
                "Xem tài khoản người khác",
                "Sửa tài khoản",
                "Sửa tài khoản người khác",
                "Xoá tài khoản",
                "Xoá tài khoản người khác",
                "Xem hoạt động tài khoản",
                "Duyệt hoạt động tài khoản",
                "Xoá hoạt động tài khoản",
                "Tạo vai trò",
                "Xem vai trò",
                "Sửa vai trò",
                "Xoá vai trò",
                "Tạo quyền hạn",
                "Xem quyền hạn",
                "Sửa quyền hạn",
                "Xoá quyền hạn",
                "Thêm vai trò tài khoản",
                "Thêm vai trò tài khoản người khác",
                "Xem vai trò tài khoản",
                "Xem vai trò tài khoản người khác",
                "Xoá vai trò tài khoản",
                "Xoá vai trò tài khoản người khác",
                "Thêm quyền hạn tài khoản",
                "Thêm quyền hạn tài khoản người khác",
                "Xem quyền hạn tài khoản",
                "Xem quyền hạn tài khoản người khác",
                "Xoá quyền hạn tài khoản",
                "Xoá quyền hạn tài khoản người khác",
                "Thêm quyền hạn vai trò",
                "Xem quyền hạn vai trò",
                "Xoá quyền hạn vai trò",
                "Tạo khách hàng",
                "Xem khách hàng",
                "Sửa khách hàng",
                "Xoá khách hàng",
                "Tạo thương hiệu",
                "Xem thương hiệu",
                "Sửa thương hiệu",
                "Xoá thương hiệu",
                "Tạo sản phẩm",
                "Xem sản phẩm",
                "Sửa sản phẩm",
                "Xoá sản phẩm",
                "Tạo phân loại sản phẩm",
                "Xem phân loại sản phẩm",
                "Sửa phân loại sản phẩm",
                "Xoá phân loại sản phẩm",
                "Xem lịch sửa giá sản phẩm",
                "Xoá lịch sử giá sản phẩm",
                "Xem quốc gia",
                "Sửa quốc gia",
                "Tạo đơn nhập hàng",
                "Xem đơn nhập hàng",
                "Sửa đơn nhập hàng",
                "Xoá đơn nhập hàng",
                "Tạo đơn hàng",
                "Xem đơn hàng",
                "Sửa đơn hàng",
                "Xoá đơn hàng",
                "Tạo khoản thanh toán đơn đặt hàng",
                "Sửa khoản thanh toán đơn đặt hàng",
                "Xoá khoản thanh toán đơn đặt hàng",
                "Tạo liệu trình",
                "Xem liệu trình",
                "Sửa liệu trình",
                "Xoá liệu trình",
                "Tạo khoản thanh toán liệu trình",
                "Sửa khoản thanh toán liệu trình",
                "Xoá khoản thanh toán liệu trình",
                "Tạo phân loại chi phí",
                "Xem phân loại chi phí",
                "Sửa phân loại chi phí",
                "Xoá phân loại chi phí",
                "Tạo người/công ty được thanh toán chi phí",
                "Xem người/công ty được thanh toán chi phí",
                "Sửa người/công ty được thanh toán chi phí",
                "Xoá người/công ty được thanh toán chi phí",
                "Tạo chi phí",
                "Xem chi phí",
                "Sửa chi phí",
                "Xoá chi phí",
                "Tạo thông báo",
                "Sửa thông báo",
                "Xoá thông báo",
            ]
            for permissionName in permissionNames:
                permission = Permission()
                permission.name = permissionName
                session.add(permission)
            session.commit()

def initializeRolePermission():
    with getDatabaseSession() as session:
        rowCount = session.scalars(
            select(func.count())
            .select_from(RolePermission)
        ).one()
        if rowCount == 0:
            rolesPermissions = {}
            rolesPermissions.update(
                {
                    "Cộng tác viên": [
                        ["Xem tài khoản",               False],
                        ["Xem vai trò",                 False],
                        ["Xem vai trò tài khoản",       False],
                        ["Xem quyền hạn tài khoản",     False],
                        ["Xem quyền hạn vai trò",       False],
                        ["Xem khách hàng",              False],
                        ["Tạo khách hàng",              False],
                        ["Xem thương hiệu",             False],
                        ["Xem sản phẩm",                False],
                        ["Xem phân loại sản phẩm",      False],
                        ["Tạo đơn hàng",                False],
                        ["Xem đơn hàng",                False],
                        ["Sửa đơn hàng",                True]
                    ]
                }
            )
            rolesPermissions.update(
                {
                    "Nhân viên": [
                        ["Xem tài khoản",                           False],
                        ["Sửa tài khoản",                           False],
                        ["Xem vai trò",                             False],
                        ["Xem vai trò tài khoản",                   False],
                        ["Tạo khách hàng",                          False],
                        ["Xem khách hàng",                          False],
                        ["Sửa khách hàng",                          True],
                        ["Xoá khách hàng",                          True],
                        ["Xem thương hiệu",                         False],
                        ["Xem sản phẩm",                            False],
                        ["Sửa sản phẩm",                            True],
                        ["Xem phân loại sản phẩm",                  False],
                        ["Xem quốc gia",                            False],
                        ["Tạo đơn nhập hàng",                       False],
                        ["Xem đơn nhập hàng",                       False],
                        ["Sửa đơn nhập hàng",                       True],
                        ["Tạo đơn hàng",                            False],
                        ["Xem đơn hàng",                            False],
                        ["Sửa đơn hàng",                            True],
                        ["Tạo liệu trình",                          False],
                        ["Xem liệu trình",                          False],
                        ["Sửa liệu trình",                          True],
                    ]
                }
            )
            rolesPermissions.update(
                {
                    "Kế toán": [
                        ["Xem tài khoản",                                       False],
                        ["Sửa tài khoản",                                       True],
                        ["Xem vai trò",                                         False],
                        ["Xem vai trò tài khoản",                               False],
                        ["Xem khách hàng",                                      False],
                        ["Xem thương hiệu",                                     False],
                        ["Xem sản phẩm",                                        False],
                        ["Xem phân loại sản phẩm",                              False],
                        ["Xem quốc gia",                                        False],
                        ["Xem đơn nhập hàng",                                   False],
                        ["Xem đơn hàng",                                        False],
                        ["Xem liệu trình",                                      False],
                        ["Tạo phân loại chi phí",                               False],
                        ["Xem phân loại chi phí",                               False],
                        ["Sửa phân loại chi phí",                               True],
                        ["Xoá phân loại chi phí",                               True],
                        ["Tạo người/công ty được thanh toán chi phí",           False],
                        ["Xem người/công ty được thanh toán chi phí",           False],
                        ["Sửa người/công ty được thanh toán chi phí",           True],
                        ["Xoá người/công ty được thanh toán chi phí",           True],
                        ["Tạo chi phí",                                         False],
                        ["Xem chi phí",                                         False],
                        ["Sửa chi phí",                                         True],
                        ["Xoá chi phí",                                         True]
                    ]
                }
            )
            rolesPermissions.update(  
                {
                    "Thu ngân": [
                        ["Xem tài khoản",                                       False],
                        ["Sửa tài khoản",                                       True],
                        ["Xem vai trò",                                         False],
                        ["Xem vai trò tài khoản",                               False],
                        ["Xem khách hàng",                                      False],
                        ["Xem thương hiệu",                                     False],
                        ["Xem sản phẩm",                                        False],
                        ["Xem phân loại sản phẩm",                              False],
                        ["Xem quốc gia",                                        False],
                        ["Xem đơn nhập hàng",                                   False],
                        ["Xem đơn hàng",                                        False],
                        ["Tạo khoản thanh toán đơn đặt hàng",                   False],
                        ["Sửa khoản thanh toán đơn đặt hàng",                   True],
                        ["Xoá khoản thanh toán đơn đặt hàng",                   True],
                        ["Xem liệu trình",                                      False],                                 
                        ["Tạo khoản thanh toán liệu trình",                     False],
                        ["Sửa khoản thanh toán liệu trình",                     True],
                        ["Xoá khoản thanh toán liệu trình",                     True],
                        ["Tạo phân loại chi phí",                               False],
                        ["Xem phân loại chi phí",                               False],
                        ["Sửa phân loại chi phí",                               True],
                        ["Xoá phân loại chi phí",                               True],
                        ["Tạo người/công ty được thanh toán chi phí",           False],
                        ["Xem người/công ty được thanh toán chi phí",           False],
                        ["Sửa người/công ty được thanh toán chi phí",           True],
                        ["Xoá người/công ty được thanh toán chi phí",           True],
                        ["Tạo chi phí",                                         False],
                        ["Xem chi phí",                                         False],
                        ["Sửa chi phí",                                         True],
                        ["Xoá chi phí",                                         True]
                    ]
                }
            )
            rolesPermissions.update(
                {
                    "Quản lý": [
                        ["Tạo tài khoản",                                       False],
                        ["Xem tài khoản",                                       False],
                        ["Xem tài khoản người khác",                            False],
                        ["Sửa tài khoản",                                       False],
                        ["Sửa tài khoản người khác",                            False],
                        ["Xoá tài khoản",                                       False],
                        ["Xoá tài khoản người khác",                            False],
                        ["Xem hoạt động tài khoản",                             False],
                        ["Duyệt hoạt động tài khoản",                           False],
                        ["Xoá hoạt động tài khoản",                             False],
                        ["Tạo vai trò",                                         False],
                        ["Xem vai trò",                                         False],
                        ["Sửa vai trò",                                         False],
                        ["Xoá vai trò",                                         False],
                        ["Tạo quyền hạn",                                       False],
                        ["Xem quyền hạn",                                       False],
                        ["Sửa quyền hạn",                                       False],
                        ["Xoá quyền hạn",                                       False],
                        ["Thêm vai trò tài khoản",                              False],
                        ["Thêm vai trò tài khoản người khác",                   False],
                        ["Xem vai trò tài khoản",                               False],
                        ["Xem vai trò tài khoản người khác",                    False],
                        ["Xoá vai trò tài khoản",                               False],
                        ["Xoá vai trò tài khoản người khác",                    False],
                        ["Thêm quyền hạn tài khoản",                            False],
                        ["Thêm quyền hạn tài khoản người khác",                 False],
                        ["Xem quyền hạn tài khoản",                             False],
                        ["Xem quyền hạn tài khoản người khác",                  False],
                        ["Xoá quyền hạn tài khoản",                             False],
                        ["Xoá quyền hạn tài khoản người khác",                  False],
                        ["Thêm quyền hạn vai trò",                              False],
                        ["Xoá quyền hạn vai trò",                               False],
                        ["Tạo khách hàng",                                      False],
                        ["Xem khách hàng",                                      False],
                        ["Sửa khách hàng",                                      False],
                        ["Xoá khách hàng",                                      False],
                        ["Tạo thương hiệu",                                     False],
                        ["Xem thương hiệu",                                     False],
                        ["Sửa thương hiệu",                                     False],
                        ["Xoá thương hiệu",                                     False],
                        ["Tạo sản phẩm",                                        False],
                        ["Xem sản phẩm",                                        False],
                        ["Sửa sản phẩm",                                        False],
                        ["Xoá sản phẩm",                                        False],
                        ["Tạo phân loại sản phẩm",                              False],
                        ["Xem phân loại sản phẩm",                              False],
                        ["Sửa phân loại sản phẩm",                              False],
                        ["Xoá phân loại sản phẩm",                              False],
                        ["Xem lịch sửa giá sản phẩm",                           False],
                        ["Xoá lịch sử giá sản phẩm",                            False],
                        ["Xem quốc gia",                                        False],
                        ["Sửa quốc gia",                                        False],
                        ["Tạo đơn nhập hàng",                                   False],
                        ["Xem đơn nhập hàng",                                   False],
                        ["Sửa đơn nhập hàng",                                   False],
                        ["Xoá đơn nhập hàng",                                   False],
                        ["Tạo đơn hàng",                                        False],
                        ["Xem đơn hàng",                                        False],
                        ["Sửa đơn hàng",                                        False],
                        ["Xoá đơn hàng",                                        False],
                        ["Tạo khoản thanh toán đơn đặt hàng",                   False],
                        ["Sửa khoản thanh toán đơn đặt hàng",                   False],
                        ["Xoá khoản thanh toán đơn đặt hàng",                   False],
                        ["Tạo liệu trình",                                      False],
                        ["Xem liệu trình",                                      False],
                        ["Sửa liệu trình",                                      False],
                        ["Xoá liệu trình",                                      False],                                    
                        ["Tạo khoản thanh toán liệu trình",                     False],
                        ["Sửa khoản thanh toán liệu trình",                     False],
                        ["Xoá khoản thanh toán liệu trình",                     False],
                        ["Tạo phân loại chi phí",                               False],
                        ["Xem phân loại chi phí",                               False],
                        ["Sửa phân loại chi phí",                               False],
                        ["Xoá phân loại chi phí",                               False],
                        ["Tạo người/công ty được thanh toán chi phí",           False],
                        ["Xem người/công ty được thanh toán chi phí",           False],
                        ["Sửa người/công ty được thanh toán chi phí",           False],
                        ["Xoá người/công ty được thanh toán chi phí",           False],
                        ["Tạo chi phí",                                         False],
                        ["Xem chi phí",                                         False],
                        ["Sửa chi phí",                                         False],
                        ["Xoá chi phí",                                         False],
                        ["Tạo thông báo",                                       False],
                        ["Sửa thông báo",                                       False],
                        ["Xoá thông báo",                                       False],
                    ]

                }
            )
            rolesPermissions.update(
                {
                    "Giám đốc": rolesPermissions["Quản lý"] 
                }
            )
            rolesPermissions.update(
                {
                    "Thành viên gia đình": rolesPermissions["Quản lý"]
                }
            )
            rolesPermissions.update(
                {
                    "Nhà phát triển": rolesPermissions["Quản lý"]
                }
            )
            
            roles: List[Role] = session.scalars(select(Role).order_by(Role.id)).all()
            for role in roles:
                if len(role.rolePermissions) > 0:
                    continue
                permissionNames = rolesPermissions[role.name]
                print(f"Intializing permissions for role <{role.name}>")
                for permissionData in permissionNames:
                    permissionName: str = permissionData[0]
                    permissionApproval: bool = permissionData[1]
                    permission = session.scalars(
                        select(Permission)
                        .where(Permission.name == permissionName)
                    ).first()
                    rolePermission = RolePermission()
                    rolePermission.roleID = role.id
                    rolePermission.permissionID = permission.id
                    rolePermission.approvalRequired = permissionApproval
                    session.add(rolePermission)
            session.commit()

def initializeSupplyAndSupplyItem():
    from app.models.supply import Supply
    from app.models.supply_item import SupplyItem
    with getDatabaseSession() as session:
        statement = select(func.count()).select_from(Supply)
        rowCount = session.scalars(statement).first()
        if rowCount == 0:
            arrivedDateTime = openingDateTime
            while arrivedDateTime <= Time.getCurrentDateTime():
                supply = Supply()
                supply.arrivedDateTime = arrivedDateTime
                supply.orderedDateTime = arrivedDateTime - timedelta(hours=randrange(24, 72))
                supply.userID = session.scalars(select(User.id).where(User.userName == "ngokhanhhuyy")).first()
                supply.shipmentFee = randrange(300000, 500000, 10000)
                supply.note = ""
                # Determind item count in supply
                itemCount = randrange(10, 15)
                productNames = []
                totalPrice = 0
                for __ in range(itemCount):
                    product: Product | None = None
                    while True:
                        product = session.scalars(select(Product).order_by(func.random())).first()
                        if product.name not in productNames:
                            break
                    item = SupplyItem()
                    item.supplyID = supply.id
                    item.productID = product.id
                    item.price = product.price * (randrange(70, 80, 2) * 0.01)
                    item.vatFactor = 0.1
                    item.suppliedQuatity = randrange(8, 20)
                    item.stockQuatity = item.suppliedQuatity
                    supply.items.append(item)
                    totalPrice += item.price
                arrivedDateTime += timedelta(days=randrange(15, 17))
                supply.paidAmount = totalPrice
                session.add(supply)
            session.commit()

def initializeOrderAndOrderItem():
    with getDatabaseSession() as session:
        statement = select(func.count()).select_from(Order)
        rowCount = session.scalars(statement).one()
        if rowCount == 0:
            usersID = session.scalars(
                select(User.id)
            ).all()
            customersID = session.scalars(
                select(Customer.id)
            ).all()
            products = session.scalars(
                select(Product)
            ).all()
            orderedDateTime = openingDateTime + timedelta(hours=randrange(3, 12))
            dayOpeningTime = time(hour=8)
            dayClosingTime = time(hour=18)
            while orderedDateTime <= Time.getCurrentDateTime():
                customerID = choice(customersID)
                userID = choice(usersID)
                order = Order()
                order.customerID = customerID
                order.userID = userID
                order.orderedDateTime = orderedDateTime
                order.deliveredDateTime = orderedDateTime + timedelta(minutes=randrange(30, 180, 30)) 
                order.shipmentFee = 0
                order.note = ""
                session.add(order)
                try:
                    session.commit()
                except Exception as exception:
                    session.rollback()
                    print(exception)
                itemCount = randrange(1, 3)
                productsAndQuatities: List[ProductAndQuatityDict] = []
                for _ in range(itemCount):
                    while True:
                        product = choice(products)
                        if product.name not in [productAndQuatity["product"].name for productAndQuatity in productsAndQuatities]:
                            productsAndQuatities.append({
                                "product": product,
                                "quatity": randrange(1, 3)
                            })
                            break
                for productAndQuatity in productsAndQuatities:
                    product: Product = productAndQuatity["product"]
                    quatity: int = productAndQuatity["quatity"]
                    selectedQuatity = 0
                    selectedSupplyItemsAndQuatity: List[SelectedOrderItemAndQuatityDict] = []
                    supplyItems = session.scalars(
                        select(SupplyItem)
                        .join(SupplyItem.supply)
                        .where(SupplyItem.productID == product.id, SupplyItem.stockQuatity > 0)
                        .order_by(Supply.arrivedDateTime)
                    ).all()
                    for selectedSupplyItem in supplyItems:
                        selectedQuatityThisItem = min(selectedSupplyItem.stockQuatity, quatity - selectedQuatity)
                        selectedSupplyItem.stockQuatity -= selectedQuatityThisItem
                        selectedQuatity += selectedQuatityThisItem
                        assert selectedSupplyItem.stockQuatity >= 0
                        selectedSupplyItemsAndQuatity.append({
                            "supplyItem":  selectedSupplyItem,
                            "quatity":     selectedQuatityThisItem
                        })
                        if selectedQuatity == quatity:
                            break
                    for selectedSupplyItemAndQuatity in selectedSupplyItemsAndQuatity:
                        selectedSupplyItem: SupplyItem = selectedSupplyItemAndQuatity["supplyItem"]
                        selectedQuatity: int = selectedSupplyItemAndQuatity["quatity"]
                        item = OrderItem()
                        item.orderID = order.id
                        item.productID = product.id
                        item.supplyItemID = selectedSupplyItem.id
                        item.price = product.price
                        item.quatity = selectedQuatity
                        item.remainingQuatity = selectedSupplyItem.stockQuatity
                        session.add(item)
                        try:
                            session.commit()
                        except Exception as exception:
                            session.rollback()
                            print(exception)
                while True:
                    orderedDateTime += timedelta(minutes=randrange(20, 180))
                    newOrderedDateTime = orderedDateTime + timedelta(minutes=randrange(20, 180))
                    if dayOpeningTime < newOrderedDateTime.time() < dayClosingTime:
                        orderedDateTime += newOrderedDateTime - orderedDateTime
                        break
                print(f"Initialized order {order.id}, ordered at {order.orderedDateTime}")

def initializeOrderPayment():
    with getDatabaseSession() as session:
        rowCount = session.scalars(
            select(func.count())
            .select_from(OrderPayment)
        ).one()
        if rowCount == 0:
            records = session.execute(
                select(Order.id, Order.userID, Order.orderedDateTime, func.sum(OrderItem.price))
                .join(Order.items)
                .order_by(Order.orderedDateTime)
                .group_by(Order.id)
            ).all()
            for record in records:
                orderID: int = record[0]
                orderUserID: int = record[1]
                orderDateTime: datetime = record[2]
                orderAmount: int = record[3]
                # Determine number of payment
                paymentTime: int = 0
                if orderAmount > 50_000_000:
                    paymentTime = 3
                elif orderAmount > 30_000_000:
                    paymentTime = 2
                else:
                    paymentTime = 1
                paidAmount = 0
                paidDateTime = orderDateTime
                for i in range(paymentTime):
                    orderPayment = OrderPayment()
                    orderPayment.orderID = orderID
                    orderPayment.paidDateTime = paidDateTime
                    orderPayment.note = ""
                    if i == 0:
                        orderPayment.userID = orderUserID
                    else:
                        orderPayment.userID = session.scalars(
                            select(User.id)
                            .join(User.roles)
                            .join(Role.rolePermissions)
                            .join(RolePermission.permission)
                            .where(
                                and_(
                                    Permission.name == "Tạo khoản thanh toán đơn đặt hàng",
                                    Role.name.in_(
                                        [
                                            "Nhân viên",
                                            "Quản lý",
                                            "Thành viên gia đình",
                                            "Nhà phát triển"
                                        ])
                                )
                            ).order_by(User.id)
                        ).first()
                    if i < paymentTime - 1:
                        orderPayment.amount = randrange(
                            (orderAmount - paidAmount) // 3,
                            (orderAmount - paidAmount) // 3 * 2)
                    else:
                        orderPayment.amount = orderAmount - paidAmount
                    paidAmount += orderPayment.amount
                    paidDateTime += timedelta(
                        days=randrange(1, 30),
                        hours=randrange(0, 23))
                    session.add(orderPayment)
                    session.flush()
            session.commit()

def initializeExpenseCategory():
    with getDatabaseSession() as session:
        rowCount = session.scalars(
            select(func.count())
            .select_from(ExpenseCategory)
        ).one()
        if rowCount == 0:
            categoryNames = [
                "Thuê văn phòng",
                "Điện",
                "Nước",
                "Intenet",
                "Trang thiết bị",
                "Vệ sinh văn phòng",
                "Vệ sinh thiết bị"
            ]
            for categoryName in categoryNames:
                expenseCategory = ExpenseCategory()
                expenseCategory.name = categoryName
                session.add(expenseCategory)
            session.commit()

def initializeExpensePayee():
    with getDatabaseSession() as session:
        rowCount = session.scalars(
            select(func.count())
            .select_from(ExpensePayee)
        ).one()
        if rowCount == 0:
            payeeNames = [
                "Công ty TNHH BĐS Thành Phát",
                "Công ty điện lực Tây Nguyên",
                "Công ty nước máy Ban Mê",
                "Công ty Cổ phần Viễn thông FPT Telecom",
                "Công ty Nội thất Văn Phòng Tiến Đạt",
                "Công ty Nội thất Cao Cấp Minh Anh",
                "Công ty Nội thất Văn Phòng Đại Phát",
                "Công ty Vệ sinh Văn Phòng Sáng Tạo",
                "Công ty Vệ sinh Thiết Bị Thành Công"
            ]
            for payeeName in payeeNames:
                expensePayee = ExpensePayee()
                expensePayee.name = payeeName
                session.add(expensePayee)
            session.commit()

def initializeExpense():
    categoriesPayees: Dict[str, str] = {
        "Thuê văn phòng":       "Công ty TNHH BĐS Thành Phát",
        "Điện":                 "Công ty điện lực Tây Nguyên",
        "Nước":                 "Công ty nước máy Ban Mê",
        "Intenet":              "Công ty Cổ phần Viễn thông FPT Telecom",
        "Trang thiết bị": [
            "Công ty Nội thất Văn Phòng Tiến Đạt",
            "Công ty Nội thất Cao Cấp Minh Anh",
            "Công ty Nội thất Văn Phòng Đại Phát"
        ],
        "Vệ sinh văn phòng":    "Công ty Vệ sinh Văn Phòng Sáng Tạo",
        "Vệ sinh thiết bị":     "Công ty Vệ sinh Thiết Bị Thành Công"
    }
    with getDatabaseSession() as session:
        rowCount = session.scalars(
            select(func.count())
            .select_from(Expense)
        ).one()
        if rowCount == 1:
            firstSellingDate = session.scalars(
                select(Order.deliveredDateTime)
                .order_by(asc(Order.deliveredDateTime))
            ).first().date()
            currentDate = firstSellingDate
            while currentDate.month < Time.getCurrentDate().month:
                for categoryName, payeeName in categoriesPayees.items():
                    expense = Expense()
                    if isinstance(payeeName, list):
                        expense.payeeID = session.scalars(
                            select(ExpensePayee.id)
                            .where(ExpensePayee.name == choice(payeeName))
                        ).one()
                    else:
                        expense.payeeID = session.scalars(
                            select(ExpensePayee.id)
                            .where(ExpensePayee.name == payeeName)
                        ).one()
                    expense.userID = session.scalars(
                        select(User.id)
                        .join(User.roles)
                        .join(Role.rolePermissions)
                        .join(RolePermission.permission)
                        .where(Permission.name == "Tạo chi phí")
                        .order_by(func.random())
                    ).first()
                    expense.categoryID = session.scalars(
                        select(ExpenseCategory.id)
                        .where(ExpenseCategory.name == categoryName)
                    ).one()
                    if categoryName == "Thuê văn phòng":
                        expense.amount = 5_000_000
                    else:
                        expense.amount = randrange(300_000, 1_000_000, 1_000)
                    expense.paidDateTime = datetime(
                        year=currentDate.year,
                        month=currentDate.month,
                        day=randrange(20, 28),
                        hour=randrange(10, 16),
                        minute=randrange(0, 59),
                        second=randrange(0, 60))
                    expense.note = ""
                    session.add(expense)
                currentDate += relativedelta(months=1)
            session.commit()

def initializeAnnouncement():
    with getDatabaseSession() as session:
        rowCount = session.scalars(
            select(func.count())
            .select_from(Announcement)
        ).one()
        if rowCount == 0:
            fakerGen = Faker()
            for _ in range(30):
                userID = session.scalars(
                    select(User.id)
                    .join(User.roles)
                    .join(Role.rolePermissions)
                    .join(RolePermission.permission)
                    .where(Permission.name == "Tạo thông báo")
                    .order_by(func.random())
                ).first()
                announcement = Announcement()
                announcement.userID = userID
                announcement.category = choice(list(Announcement.Categories))
                announcement.title = fakerGen.paragraph(nb_sentences=1)
                announcement.content = fakerGen.paragraph(nb_sentences=15)
                announcement.startingDateTime = Time.getCurrentDateTime()
                announcement.endingDateTime = Time.getCurrentDateTime() + timedelta(days=10000)
                session.add(announcement)
            session.commit()

def initializePhoto():
    with getDatabaseSession() as session:
        rowCount = session.scalars(
            select(func.count())
            .select_from(Photo)
        ).one()
        if rowCount == 0:
            photoCountChance = ([0] * 30) + ([1] * 10) + ([2] * 5) + ([3] * 3) + [4, 4, 5]
            # Users
            userID = session.scalars(
                select(User.id)
                .where(User.userName == "ngokhanhhuyy")
            ).first()
            with open("app/static/profile_pictures/staff_1.jpg", "rb") as photoFile:
                binaryData = photoFile.read()
                photo = Photo()
                photo.content = binaryData
                photo.isPrimary = True
                photo.userID = userID
                session.add(photo)
                session.flush()
                print(f"Initialized profile picture {photo.id} for user {userID}")
            # Customers
            customers = session.scalars(
                select(Customer)
                .outerjoin(Customer.photos)
                .order_by(Customer.id)
            ).all()
            profilePictureID = 1
            photoID = 1
            for customer in customers:
                hasProfilePicture = randrange(0, 2)
                photoCount = choice(photoCountChance)
                # Profile picture
                if hasProfilePicture:
                    with open(f"app/static/photos/profile_pictures/{profilePictureID}.jpeg", "rb") as profilePictureFile:
                        customer.photos.append(Photo(
                            isPrimary=True,
                            content=profilePictureFile.read()
                        ))
                    if profilePictureID + 1 > 1000:
                        profilePictureID = 1
                    else:
                        profilePictureID += 1
                # Secondary photos
                for _ in range(photoCount):
                    with open(f"app/static/photos/{photoID}.jpeg", "rb") as photoFile:
                        customer.photos.append(Photo(
                            isPrimary=False,
                            content=photoFile.read()
                        ))
                    if photoID + 1 > 1000:
                        photoID = 1
                    else:
                        photoID += 1
                session.flush()
                print(f"Initialized photos for customer {customer.id}")
            session.commit()
        
class ProductAndQuatityDict:
    product: Product
    quatity: int

class SelectedOrderItemAndQuatityDict:
    supplyItem: SupplyItem
    quatity: int


        