from sanic import Request, HTTPResponse
from functools import wraps
from sanic.exceptions import Unauthorized
from middleware.auth import verify_token
import jwt
import time
from models.user import User

def jwt_required(wrapped):
    """JWT 验证装饰器"""
    @wraps(wrapped)
    async def decorated_function(request, *args, **kwargs):
        # 从请求头中获取令牌
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise Unauthorized('缺少有效的授权令牌')
        
        token = auth_header.split(' ')[1]
        user = await verify_token(request, token)
        
        if not user:
            raise Unauthorized('无效的授权令牌')
        
        # 将用户信息添加到请求对象
        request.ctx.user = user
        return await wrapped(request, *args, **kwargs)
    
    return decorated_function

def inject_user(middleware_or_route):
    """注入用户信息中间件，但不强制要求验证"""
    @wraps(middleware_or_route)
    async def wrapped_function(request, *args, **kwargs):
        # 从请求头中获取令牌
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user = await verify_token(request, token)
            if user:
                request.ctx.user = user
        
        return await middleware_or_route(request, *args, **kwargs)
    
    return wrapped_function

async def add_user_to_request(request):
    """
    JWT中间件：验证token并将用户添加到请求上下文
    """
    try:
        # 获取Authorization头
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
            
            # 验证token
            payload = jwt.decode(
                token, 
                request.app.config.JWT_SECRET, 
                algorithms=["HS256"]
            )
            
            # 检查token是否过期
            if payload.get('exp') and payload.get('exp') < time.time():
                request.ctx.user = None
                return None
                
            # 获取用户
            user_id = payload.get('user_id')
            if user_id:
                user = await User.get_or_none(id=user_id)
                request.ctx.user = user
                return None
                
        request.ctx.user = None
    except jwt.PyJWTError:
        request.ctx.user = None
    except Exception as e:
        print(f"JWT错误: {str(e)}")
        request.ctx.user = None
        
    return None

def generate_tokens(user_id, app_config):
    """
    生成访问令牌和刷新令牌
    """
    # 设置过期时间
    access_token_expires = time.time() + app_config.JWT_ACCESS_TOKEN_EXPIRES
    refresh_token_expires = time.time() + app_config.JWT_REFRESH_TOKEN_EXPIRES
    
    # 生成访问令牌
    access_token = jwt.encode(
        {
            'user_id': user_id,
            'exp': access_token_expires,
            'type': 'access'
        },
        app_config.JWT_SECRET,
        algorithm='HS256'
    )
    
    # 生成刷新令牌
    refresh_token = jwt.encode(
        {
            'user_id': user_id,
            'exp': refresh_token_expires,
            'type': 'refresh'
        },
        app_config.JWT_SECRET,
        algorithm='HS256'
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': app_config.JWT_ACCESS_TOKEN_EXPIRES
    }

async def verify_refresh_token(refresh_token, app_config):
    """
    验证刷新令牌并返回用户ID
    """
    try:
        payload = jwt.decode(
            refresh_token, 
            app_config.JWT_SECRET, 
            algorithms=["HS256"]
        )
        
        # 检查令牌类型
        if payload.get('type') != 'refresh':
            raise ValueError("无效的刷新令牌")
            
        # 检查令牌是否过期
        if payload.get('exp') and payload.get('exp') < time.time():
            raise ValueError("刷新令牌已过期")
            
        # 返回用户ID
        return payload.get('user_id')
    except (jwt.PyJWTError, ValueError) as e:
        raise ValueError(f"刷新令牌验证失败: {str(e)}") 