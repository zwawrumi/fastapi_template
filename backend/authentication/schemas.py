import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, constr, validator


class TunedModel(BaseModel):
    class Config:
        """pydantic convert to json"""

        from_attributes = True


class ShowUser(TunedModel):
    user_id: uuid.UUID
    username: str
    email: EmailStr
    is_active: Optional[bool] = True


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @validator('username')
    def validate_username(cls, value):
        if not value.isalnum():
            raise ValueError('Username should contain only letters and digits')
        return value


class DeleteUser(BaseModel):
    deleted_user_id: uuid.UUID


class UpdatedUser(BaseModel):
    updated_user_id: uuid.UUID


class UpdateUserRequest(BaseModel):
    username: Optional[constr(min_length=5)]
    email: Optional[EmailStr]

    @validator('username')
    def validate_username(cls, value):
        if not value.isalnum():
            raise ValueError('Username should contain only letters and digits')
        return value


class UpdatedUserResponse(BaseModel):
    updated_user_id: uuid.UUID


class Token(BaseModel):
    access_token: str
    token_type: str
