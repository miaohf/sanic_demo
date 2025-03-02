from sanic_jwt.exceptions import AuthenticationFailed
from models.user import User

async def authenticate(request, *args, **kwargs):
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username or not password:
        raise AuthenticationFailed("Missing username or password")

    user = await User.query.where(User.username == username).gino.first()
    if user and user.password == password:  # 实际使用时应该用密码哈希比较
        return user

    raise AuthenticationFailed("Invalid username or password") 