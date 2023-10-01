from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from enum import Enum
from typing import Any

class SQLModelValidationError(Exception):
    pass
    # def __init__(self, field: str, value: Any) -> None:
    #     self.field = field
    #     self.value = value


class SQLModelOperationError(Exception):
    def __init__(self):
        self.field = None
        self.value = None

    @classmethod
    def fromSQLAlchemyException(cls, exception: SQLAlchemyError) -> "SQLModelOperationError":
          pass


class Validations:
    class Users:
        # Username
        UserNameMinLength = 6
        UserNameMaxLength = 20
        # Password
        PasswordMinLength = 8
        PasswordContainsNumericCharacter = False
        PasswordContainsUpperCaseLetter = False
        PasswordContainsSymbols = False
        # FullName
        FullNameMinLength = 1
        FullNameMaxLength = 35
        # NickName
        NickNameMaxLength = 35
        # Phone
        PhoneMaxLength = 15
        # Email
        EmailMaxLength = 255
        # Zalo
        ZaloMaxLength = 15
        # Facebook
        FacebookURLContainsDomain = True
        # ID Card Number
        IDCardNumberMaxLength = 12

    class UserRoles:
        # Name
        NameMaxLength = 20

    class Customers:
        # Fullname
        FullNameMinLength = 1
        FullNameMaxLength = 35
        # NickName
        NickNameMaxLength = 35
        # Company
        CompanyMaxLength = 50
        # Phone
        PhoneMaxLength = 15
        # Email
        EmailMaxLength = 255
        # Zalo
        ZaloMaxLength = 15
        # Facebook
        FacebookURLContainsDomain = True
    
    class Brands:
        # Name
        NameMaxLength = 50
        NameMinLength = 1
        # Phone
        PhoneMaxLength = 15
        # Email
        EmailMaxLength = 255

    class Products:
        # Name
        NameMaxLength = 50
        NameMinLength = 1
        UnitMaxLength = 20
        UnitMinLength = 1

    class ProductCategories:
        # Name
        NameMaxLength = 30

