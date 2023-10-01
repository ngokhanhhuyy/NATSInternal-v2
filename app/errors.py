from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation, UniqueViolation
from pydantic import ValidationError
from typing import *

class ErrorCodes:
    AuthenticationError = "ERR100"
    AuthorizationError = "ERR101"
    RequestValidationError = "ERR102"
    DataValidationError = "ERR103"
    DataOprationError = "ERR104"
    NotFoundError = "ERR105"

class TranslatedText:
    Vietnamese: Dict[str, Dict[str, str]] = {
        "product":      {
            "name":     "Sản phẩm",
            "fields":   {
                "id":                   "Định danh",
                "name":                 "Tên",
                "brandIdentity":        "Thương hiệu",
                "categoryIdentity":     "Phân loại",
                "description":          "Mô tả",
                "unit":                 "Đơn vị",
                "publishedPrice":       "Giá niêm yết",
                "vatFactor":            "Hệ số thuế",
                "createdDateTime":      "Thời gian tạo",
                "updatedDateTime":      "Thời gian chỉnh sửa",
                "thumbnail":            "Ảnh đại diện",
                "photos":               "Ảnh"
            },
        },
        "productPriceHistory":      {
            "name":     "Lịch sử giá sản phẩm",
            "fields":   {
                "id":                   "Định danh",
                "productIdentity":      "Định danh sản phẩm",
                "publishedPrice":       "Giá niêm yết",
                "vatFactor":            "Hệ số VAT",
                "loggedDateTime":       "Ngày điều chỉnh",
                "changedType":          "Loại thay đổi"
            }
        }
    }

class NATSException(Exception):
    def toDictionary(self):
        pass

class AuthenticationError(NATSException):
    def __init__(self, text: str):
        self.errorCode = ErrorCodes.AuthenticationError
        self.errorName = "Lỗi xác thực"
        self.text = text

    def toDictionary(self) -> Dict[str, str]:
        return {
            "errorCode":            self.errorCode,
            "errorName":            self.errorName,
            "text":                 self.text
        }

class AuthorizationError(NATSException):
    def __init__(
        self,
        action: str = None,
        modelName: str = None,
        id: int = None,
        name: str = None
    ):
        self.errorCode = ErrorCodes.AuthorizationError
        self.errorName = "Lỗi phân quyền"
        self.modelName = modelName
        self.id = id
        self.name = name
        self.action = action
        self.text = ""
        if action is not None:
            if self.modelName is not None:
                if self.id is not None or self.name is not None:
                    self.text = (f"Bạn không có quyền {action} "
                                f"dữ liệu của {modelName.lower()} '{name}'.")
                else:
                    self.text = (f"Bạn không có quyền {action.lower()} "
                                f"dữ liệu của {modelName.lower()} này.")
            else:
                self.text = (f"Bạn không có quyền {action.lower()} dữ liệu "
                            f"của mục {modelName.lower()}.")
        else:
            self.text = "Bạn không có quyền thực hiện yêu càu này."

    def toDictionary(self) -> Tuple[Dict[str, str], int]:
        return {
            "errorCode":            self.errorCode,
            "errorName":            self.errorName,
            "model":                self.modelName,
            "id":                   self.id,
            "name":                 self.name,
            "action":               self.action,
            "text":                 self.text
        }, 401
    
class RequestValidationError(NATSException):
    def __init__(self, exception: ValidationError):
        self.errorCode = ErrorCodes.RequestValidationError
        self.errorName = "Yêu tới máy chủ không hợp lệ"
        self.errorFields = []
        for field in exception.errors():
            self.errorFields.append(field["loc"][0])
        self.exceptionString = str(exception)
        self.text = ("Yêu cầu gửi tới máy chủ không đúng định dạng hoặc chứa dữ liệu không hợp lệ.\n"
                    "Nguyên nhân của lỗi này có thể do lỗi phần mềm. Hãy liên hệ nhà phát triển để khắc phục.\n"
                    f"Mã lỗi: {self.errorCode}")
        
    def toDictionary(self) -> Tuple[Dict[str, str], int]:
        return {
            "errorCode":            self.errorCode,
            "errorName":            self.errorName,
            "errorFields":          self.errorFields,
            "exceptionString":      self.exceptionString,
            "text":                 self.text,
        }, 415

class DataValidationError(NATSException):
    def __init__(self, modelName: str, fieldName: str, rule: str):
        self.errorCode = ErrorCodes.DataValidationError
        self.errorName = "Dữ liệu không hợp lệ"
        self.modelName = modelName
        self.fieldName = fieldName
        self.rule = rule

    def toDictionary(self) -> Tuple[Dict[str, str], int]:
        return {
            "errorCode":        self.errorCode,
            "errorName":        self.errorName,
            "model":            self.modelName,
            "field":            self.fieldName,
            "rule":             self.rule
        }, 400

class DataOperationError(NATSException):
    def __init__(self, exception: IntegrityError):
        exceptionString: str = exception.args[0]
        violation = exception.orig
        self.errorCode = ErrorCodes.DataOprationError
        self.errorName = "Dữ liệu không hợp lệ"
        self.modelName = exception.orig.diag.table_name
        self.fieldName = None
        self.value = exceptionString.split("\n")[1].split("(")[2].split(")")[0]
        self.errorCode = ErrorCodes.DataOprationError
        self.vietnameseText = "Dữ liệu không hợp lệ"
        vnModelName = TranslatedText.Vietnamese[self.modelName]["name"].lower()
        self.text = ""
        print(str(violation))
        if isinstance(violation, ForeignKeyViolation):
            self.fieldName = exceptionString.split("\n")[1].split("(")[1].split(")")[0]
            vnFieldName = TranslatedText.Vietnamese[self.modelName]["fields"][self.fieldName]
            self.text = (f"{vnFieldName} {vnModelName} không tồn tại.\n"
                        "Lỗi này có thể là lỗi do phần mềm. Vui lòng liên hệ nhà phát triển để khắc phục.\n"
                        f"Mã lỗi: {self.errorCode}")
        elif isinstance(violation, UniqueViolation):
            self.fieldName = exceptionString.split("\n")[1].split("(")[1].split(")")[0]
            vnFieldName = TranslatedText.Vietnamese[self.modelName]["fields"][self.fieldName]
            self.text = f"{vnFieldName} {vnModelName} đã tồn tại. Vui lòng sử dụng {vnFieldName.lower()} khác."
    
    def toDictionary(self) -> Tuple[Dict[str, str], int]:
        return {
            "errorCode":        self.errorCode,
            "errorName":        self.errorName,
            "model":            self.modelName,
            "field":            self.fieldName,
            "value":            self.value,
            "text":             self.text,
        }, 400

class NotFoundError(NATSException):
    def __init__(self, modelName: str, id: int):
        vnModelName = TranslatedText.Vietnamese[modelName]["name"].lower()
        self.errorCode = ErrorCodes.NotFoundError
        self.errorName = f"Không tìm thấy {vnModelName}"
        self.modelName = modelName
        self.id = id
        self.text = f"{vnModelName} không tồn tại. Vui lòng kiểm tra lại."

    def toDictionary(self) -> Tuple[Dict[str, str], int]:
        return {
            "errorCode":        self.errorCode,
            "errorName":        self.errorName,
            "model":            self.modelName,
            "id":               self.id,
            "text":             self.text,
        }, 404