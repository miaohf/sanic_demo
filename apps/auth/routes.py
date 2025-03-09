from sanic import Blueprint
from sanic.views import HTTPMethodView
from sanic.response import json
from sanic_ext import openapi
from middleware.jwt_middleware import generate_tokens, verify_refresh_token
from models.user import User
import bcrypt

bp = Blueprint('auth', url_prefix='/auth')

class AuthView(HTTPMethodView):
    @openapi.summary("用户登录")
    @openapi.description("用户登录并返回访问令牌和刷新令牌")
    @openapi.body({"username": str, "password": str})
    @openapi.response(200, {"access_token": str, "refresh_token": str, "expires_in": int})
    @openapi.response(401, {"error": str})
    async def post(self, request):
        try:
            data = request.json
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return json({"error": "用户名和密码不能为空"}, status=400)
            
            # 查找用户
            user = await User.get_or_none(username=username)
            if not user:
                return json({"error": "用户名或密码不正确"}, status=401)
            
            # 验证密码
            if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                return json({"error": "用户名或密码不正确"}, status=401)
            
            # 生成令牌
            tokens = generate_tokens(user.id, request.app.config)
            
            return json(tokens)
        except Exception as e:
            return json({"error": str(e)}, status=500)

class TokenRefreshView(HTTPMethodView):
    @openapi.summary("刷新令牌")
    @openapi.description("使用刷新令牌获取新的访问令牌")
    @openapi.body({"refresh_token": str})
    @openapi.response(200, {"access_token": str, "refresh_token": str, "expires_in": int})
    @openapi.response(401, {"error": str})
    async def post(self, request):
        try:
            data = request.json
            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                return json({"error": "刷新令牌不能为空"}, status=400)
            
            # 验证刷新令牌
            user_id = await verify_refresh_token(refresh_token, request.app.config)
            
            # 检查用户是否存在
            user = await User.get_or_none(id=user_id)
            if not user:
                return json({"error": "用户不存在或已被删除"}, status=401)
            
            # 生成新令牌
            tokens = generate_tokens(user.id, request.app.config)
            
            return json(tokens)
        except ValueError as e:
            return json({"error": str(e)}, status=401)
        except Exception as e:
            return json({"error": str(e)}, status=500)

# 注册路由
bp.add_route(AuthView.as_view(), "/login")
bp.add_route(TokenRefreshView.as_view(), "/refresh") 