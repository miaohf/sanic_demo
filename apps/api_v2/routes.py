from sanic import Blueprint
from sanic.response import json
from sanic_ext import openapi
from sanic_jwt.decorators import protected

from models.user import User

bp = Blueprint('v2', url_prefix='/api/v2')

@bp.route("/users", methods=["GET"])
@openapi.summary("获取用户列表（v2）")
@openapi.description("返回所有用户的详细信息列表，包括创建时间")
@openapi.response(200, {"users": [{"id": int, "username": str, "email": str, "created_at": str}]})
@protected()
async def get_users(request):
    users = await User.query.gino.all()
    return json([{
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": str(user.created_at)
    } for user in users])

@bp.route("/users/<user_id:int>", methods=["GET"])
@openapi.summary("获取单个用户信息")
@openapi.description("根据用户ID返回用户详细信息")
@openapi.response(200, {"user": {"id": int, "username": str, "email": str, "created_at": str}})
@protected()
async def get_user(request, user_id):
    user = await User.get(user_id)
    if not user:
        return json({"error": "用户不存在"}, status=404)
    
    return json({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": str(user.created_at)
    })

@bp.route("/users", methods=["POST"])
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
async def create_user(request):
    data = request.json
    
    # 检查用户名是否已存在
    existing_user = await User.query.where(User.username == data['username']).gino.first()
    if existing_user:
        return json({"error": "用户名已存在"}, status=400)
    
    # 创建新用户
    user = await User.create(
        username=data['username'],
        password=data['password'],  # 实际应用中需要对密码进行哈希处理
        email=data['email']
    )
    
    return json({
        "id": user.id,
        "username": user.username,
        "email": user.email
    }, status=201)

@bp.route("/users/<user_id:int>", methods=["DELETE"])
@openapi.summary("删除用户")
@openapi.description("根据用户ID删除用户")
@protected()
async def delete_user(request, user_id):
    user = await User.get(user_id)
    if not user:
        return json({"error": "用户不存在"}, status=404)
    
    await user.delete()
    return json({"message": "用户已删除"}) 