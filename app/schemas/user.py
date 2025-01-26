from enum import Enum
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    email: str = Field(pattern=r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$")


class GetAllUsersResponse(UserBase):
    isAdmin: bool
    id: str


class CreateUser(UserBase):
    password: str


class LoginUser(UserBase):
    password: str


class DeleteUser(BaseModel):
    id: str


# use Pydantic to make schema
