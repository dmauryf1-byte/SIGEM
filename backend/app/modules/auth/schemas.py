from pydantic import BaseModel, ConfigDict, Field

from app.modules.users.models import Role


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    role: Role


class LoginResponse(BaseModel):
    user: UserOut
