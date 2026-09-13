from pydantic import BaseModel, Field

from app.schemas.user_schemas import UserOut


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    message: str
    session_id: str
    user: UserOut