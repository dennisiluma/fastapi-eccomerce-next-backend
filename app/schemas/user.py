from time import strftime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic.alias_generators import to_camel

from app.models.user import UserRole



class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: Optional[UserRole] = UserRole.CUSTOMER



class UserRead(BaseModel):
    id: int
    email: str
    name: str
    role: UserRole
    active: bool
    profile_picture: Optional[str] = None 
    address: Optional[str] = None 
    

    model_config =ConfigDict(
        alias_generator=to_camel, #automatically convert python snake_case to carmelCase e.g profile_picture -> profilePicture
        populate_by_name=True, #allow you create an object eitjer using the alias(e.g profilePicture) or original name( e,g profile_picture)
        from_attributes=True #allow you read data directly from database. i.e allows you to pass a raw database object directly into your model
    )



class UserLogin(BaseModel):
    email: EmailStr
    password: str



class TokenData(BaseModel):
    token: str
    type: str = "bearer"
    user: UserRead



class UserUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None



class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

    model_config =ConfigDict(
        alias_generator=to_camel, #automatically convert python snake_case to carmelCase e.g old_password -> oldPassword
        populate_by_name=True, #allow you create an object eitjer using the alias(e.g oldPassword) or original name( e,g old_password)
        from_attributes=True #allow you read data directly from database. i.e allows you to pass a raw database object directly into your model
    )



class ForgotPasswordRequest(BaseModel):
    email: EmailStr



class ResetPasswordRequest(BaseModel):
    code: str
    password: str