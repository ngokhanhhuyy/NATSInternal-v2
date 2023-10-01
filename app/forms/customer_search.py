from wtforms import *
from flask_wtf import FlaskForm

class CustomerSearchForm(FlaskForm):
    page = IntegerField("Số trang", default=1)
    searchContent = SearchField("Nội dung", validators=[validators.DataRequired()])
    searchField = SelectField(
        "Tìm theo",
        choices=[
            ("fullName", "Họ và tên"),
            ("firstName", "Họ"),
            ("lastName", "Tên"),
            ("phone", "Số điện thoại")
        ],
        default="fullName")