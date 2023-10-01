from marshmallow import Schema, fields, ValidationError, validate, EXCLUDE

class CustomerSortValidator(Schema):
    page = fields.Integer(
        required=False,
        allow_none=True,
        missing=1,
        validate=validate.Range(
            min=1,
            error="Số trang phải lớn hơn hoặc bằng 1."),
        error_messages={
            "null":         "Số trang không được chứa giá trị None.",
            "required":     "Số trang không được để trống."
        })
    sortByField = fields.String(
        required=False,
        missing="lastName",
        allow_none=False,
        validate=validate.OneOf(
            choices=["firstName", "lastName", "birthday", "createdDateTime"],
            error="Trường sắp xếp không hợp lệ."))
    sortOrder = fields.String(
        required=False,
        missing="ascending",
        allow_none=False,
        validate=validate.OneOf(
            choices=["ascending", "descending"],
            error="Thứ tự sắp xếp không hợp lệ."),
        error_messages={
            "null":         "Thứ tự sắp xếp không chấp nhận giá trị None."
        })
    
    class Meta:
        unknown = EXCLUDE