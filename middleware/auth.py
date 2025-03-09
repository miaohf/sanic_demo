import jwt
import uuid
from datetime import datetime, timedelta
from sanic_jwt.exceptions import AuthenticationFailed
from models.user import User
from tortoise.exceptions import DoesNotExist

# JWT 配置
JWT_SECRET = "your-very-secret-and-very-long-random-key-here"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
ALGORITHM = "HS256"

async def authenticate(request, *args, **kwargs):
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username or not password:
        raise AuthenticationFailed("缺少用户名或密码")

    try:
        user = await User.get(username=username)
        if not await user.verify_password(password):
            raise AuthenticationFailed("用户名或密码无效")
            
        # 更新登录时间
        user.last_login = datetime.utcnow()
        await user.save()
            
        # 生成 refresh token
        refresh_token = str(uuid.uuid4())
        user.refresh_token = refresh_token
        await user.save()
            
        # 返回用户信息用于生成 JWT
        return {"user_id": user.id, "refresh_token": refresh_token}
            
    except DoesNotExist:
        raise AuthenticationFailed("用户名或密码无效")

def generate_tokens(user_id, refresh_token=None):
    """生成访问令牌和刷新令牌"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    expire = datetime.utcnow() + access_token_expires
    access_payload = {
        "user_id": user_id,
        "exp": expire,
        "type": "access"
    }
    
    access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=ALGORITHM)
    
    if not refresh_token:
        refresh_token = str(uuid.uuid4())
    
    refresh_expire = datetime.utcnow() + refresh_token_expires
    refresh_payload = {
        "user_id": user_id,
        "refresh_token": refresh_token,
        "exp": refresh_expire,
        "type": "refresh"
    }
    
    refresh_token_encoded = jwt.encode(refresh_payload, JWT_SECRET, algorithm=ALGORITHM)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_encoded,
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

async def refresh_token(request):
    """使用刷新令牌生成新的访问令牌"""
    refresh_token = request.json.get("refresh_token", None)
    
    if not refresh_token:
        raise AuthenticationFailed("缺少刷新令牌")
    
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[ALGORITHM])
        
        if payload["type"] != "refresh":
            raise AuthenticationFailed("无效的令牌类型")
        
        user_id = payload["user_id"]
        token_str = payload["refresh_token"]
        
        # 验证 refresh token 是否与用户存储的匹配
        user = await User.get(id=user_id)
        if user.refresh_token != token_str:
            raise AuthenticationFailed("刷新令牌已失效")
        
        # 生成新的 token
        tokens = generate_tokens(user_id, token_str)
        return tokens
        
    except jwt.PyJWTError:
        raise AuthenticationFailed("无效的刷新令牌")
        
async def verify_token(request, token):
    """验证 JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id = payload["user_id"]
        
        if payload["type"] != "access":
            return None
            
        # 验证用户是否存在
        user = await User.get(id=user_id)
        return user
    except (jwt.PyJWTError, DoesNotExist):
        return None 