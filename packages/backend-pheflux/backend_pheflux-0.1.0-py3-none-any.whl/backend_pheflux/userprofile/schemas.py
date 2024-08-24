from ninja import Schema
from pydantic import validator

class UserIn(Schema):
    username: str
    email: str
    password: str
    phone_number: str = None

    @validator('phone_number', pre=True, always=True)
    def format_phone_number(cls, v):
        return str(v) if v else ""

class UserOut(Schema):
    id: int
    username: str
    email: str
    phone_number: str

    @validator('phone_number', pre=True, always=True)
    def format_phone_number(cls, v):
        return str(v) if v else ""

class ChangePasswordIn(Schema):
    old_password: str
    new_password: str
