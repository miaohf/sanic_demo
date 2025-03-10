from sanic import Blueprint
from sanic.views import HTTPMethodView
from sanic.response import json
from sanic_ext import openapi
from sanic_jwt.decorators import protected, inject_user
from tortoise.exceptions import DoesNotExist
from pydantic import BaseModel, EmailStr, Field

from models.user import User

bp = Blueprint('v2', url_prefix='/api/v2')

# Pydantic 模型用于请求验证和响应序列化
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: str

class UsersView(HTTPMethodView):
    @openapi.summary("获取用户列表（v2）")
    @openapi.description("返回所有用户的详细信息列表，包括创建时间")
    @openapi.response(200, {"users": [{"id": int, "username": str, "email": str, "created_at": str}]})
    @protected()
    async def get(self, request):
        users = await User.all()
        return json({
            "users": [{
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": str(user.created_at)
            } for user in users]
        })
    
    @openapi.summary("创建新用户")
    @openapi.description("创建一个新用户")
    @openapi.body(
        {
            "username": str,
            "password": str,
            "email": str
        },
        description="用户信息",
        required=True
    )
    @openapi.response(201, {"id": int, "username": str, "email": str})
    async def post(self, request):
        # 使用 pydantic 验证
        try:
            user_data = UserCreate(**request.json)
        except ValueError as e:
            return json({"error": str(e)}, status=400)
        
        # 检查用户名是否已存在
        existing_user = await User.filter(username=user_data.username).first()
        if existing_user:
            return json({"error": "用户名已存在"}, status=400)
        
        # 创建新用户
        user = await User.create(
            username=user_data.username,
            password=user_data.password,  # 实际应用中需要对密码进行哈希处理
            email=user_data.email
        )
        
        return json({
            "id": user.id,
            "username": user.username,
            "email": user.email
        }, status=201)

class UserDetailView(HTTPMethodView):
    @openapi.summary("获取单个用户信息")
    @openapi.description("根据用户ID返回用户详细信息")
    @openapi.response(200, {"user": {"id": int, "username": str, "email": str, "created_at": str}})
    @protected()
    async def get(self, request, user_id):
        try:
            user = await User.get(id=user_id)
            return json({
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "created_at": str(user.created_at)
                }
            })
        except DoesNotExist:
            return json({"error": "用户不存在"}, status=404)
    
    @openapi.summary("删除用户")
    @openapi.description("根据用户ID删除用户")
    @protected()
    async def delete(self, request, user_id):
        try:
            user = await User.get(id=user_id)
            await user.delete()
            return json({"message": "用户已删除"})
        except DoesNotExist:
            return json({"error": "用户不存在"}, status=404)

# 注册路由
bp.add_route(UsersView.as_view(), "/users")
bp.add_route(UserDetailView.as_view(), "/users/<user_id:int>") 