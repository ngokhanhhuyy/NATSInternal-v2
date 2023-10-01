from wtforms import *
from flask_wtf import FlaskForm

class CustomerSortForm(FlaskForm):
    page = IntegerField(
        "Số trang",
        default=1,
        validators=[validators.NumberRange(min=1)])
    sortByField = SelectField(
        "Sắp xếp theo",
        choices=[
            ("lastName", "Tên"),
            ("firstName", "Họ"),
            ("birthday", "Ngày sinh"),
            ("createdDateTime", "Ngày tạo")
        ],
        default="lastName",
        validators=[validators.Optional()])
    sortOrder = SelectField(
        "Thứ tự",
        choices=[
            ("ascending", "Từ nhỏ đến lớn"),
            ("descending", "Từ lớn đến nhỏ")
        ],
        default="ascending",
        validators=[validators.Optional()])