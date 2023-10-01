from wtforms import *

class LoginFormModel(Form):
    userName = StringField(
        "Tên đăng nhập",
        validators=[
            validators.DataRequired(message="Tên đăng nhập không được để trống.")])
    password = PasswordField(
        "Mật khẩu",
        validators=[validators.DataRequired(message="Mật khẩu không được để trống.")])