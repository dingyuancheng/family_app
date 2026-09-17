from pydantic import BaseModel, Field

from app.schemas.user_schemas import UserOut


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    message: str
    session_id: str
    user: UserOut


class LogoutResponse(BaseModel):
    message: str = "已退出登录"


class ServerConfigResponse(BaseModel):
    default_domain: str = "http://192.168.0.6:8000"
    backup_domain: str = ""
    app_version: str = "0.1.0"