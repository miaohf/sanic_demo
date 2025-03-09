from sanic.views import HTTPMethodView
from sanic.response import json
from sanic_ext import openapi
from schemas.user import UserCreate, UserResponse
from models.user import User
from middleware.jwt_middleware import jwt_required
from tortoise.exceptions import IntegrityError

class UserView(HTTPMethodView):
    @openapi.summary("获取用户列表")
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
    @openapi.body({"username": str, "password": str, "email": str})
    @openapi.response(201, {"id": int, "username": str, "email": str})
    @jwt_required
    async def post(self, request):
        try:
            # 验证请求数据
            data = request.json
            user_data = UserCreate(**data)
            
            # 检查用户名是否已存在
            existing_user = await User.filter(username=user_data.username).first()
            if existing_user:
                return json({"error": "用户名已存在"}, status=400)
            
            # 创建新用户
            user = await User.create(
                username=user_data.username,
                password=user_data.password,  # 密码哈希将在save方法中处理
                email=user_data.email
            )
            
            # 返回创建的用户信息
            return json({
                "id": user.id,
                "username": user.username,
                "email": user.email
            }, status=201)
            
        except Exception as e:
            return json({"error": f"创建用户失败: {str(e)}"}, status=500)

class UserDetailView(HTTPMethodView):
    @openapi.summary("获取用户详情")
    async def get(self, request, user_id):
        user = await User.get_or_none(id=user_id)
        if not user:
            return json({"error": "用户不存在"}, status=404)
            
        return json({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": str(user.created_at)
        })
        
    @openapi.summary("更新用户")
    @jwt_required
    async def put(self, request, user_id):
        # 只能更新自己的信息
        if str(request.ctx.user.id) != str(user_id):
            return json({"error": "没有权限"}, status=403)
            
        user = await User.get_or_none(id=user_id)
        if not user:
            return json({"error": "用户不存在"}, status=404)
            
        data = request.json
        if data.get('username') and data['username'] != user.username:
            # 检查新用户名是否已存在
            existing_user = await User.filter(username=data['username']).first()
            if existing_user:
                return json({"error": "用户名已存在"}, status=400)
            user.username = data['username']
            
        if data.get('email'):
            user.email = data['email']
            
        if data.get('password'):
            user.password = data['password']  # 哈希处理在save方法中
            
        await user.save()
        
        return json({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "updated_at": str(user.updated_at)
        })
        
    @openapi.summary("删除用户")
    @jwt_required
    async def delete(self, request, user_id):
        # 只能删除自己的账户
        if str(request.ctx.user.id) != str(user_id):
            return json({"error": "没有权限"}, status=403)
            
        user = await User.get_or_none(id=user_id)
        if not user:
            return json({"error": "用户不存在"}, status=404)
            
        await user.delete()
        return json({"message": "用户已删除"}) 