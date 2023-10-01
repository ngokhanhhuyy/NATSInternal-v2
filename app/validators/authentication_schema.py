from app.validation import Validations
from typing import Dict
from pydantic import BaseModel, constr

class AuthenticationSchema(BaseModel):
    userName: constr(min_length=1)
    password: constr(min_length=1)