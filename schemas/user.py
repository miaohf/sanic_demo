from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    
    # Pydantic v2 的新配置方式
    model_config = {
        "from_attributes": True  # 替代v1中的orm_mode=True
    }

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int 