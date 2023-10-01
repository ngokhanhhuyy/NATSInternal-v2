from enum import StrEnum, unique

@unique
class Sexes(StrEnum):
    Undefined = "Không xác định"
    Male = "Nam"
    Female = "Nữ"