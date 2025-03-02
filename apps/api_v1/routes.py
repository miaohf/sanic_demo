from sanic import Blueprint
from sanic.response import json
from sanic_ext import openapi
from models.user import User

bp = Blueprint('v1', url_prefix='/api/v1')

@bp.route("/users", methods=["GET"])
@openapi.summary("获取用户列表")
@openapi.description("返回所有用户的列表")
@openapi.response(200, {"users": [{"id": int, "username": str, "email": str}]})
async def get_users(request):
    users = await User.all()
    return json([{
        "id": user.id,
        "username": user.username,
        "email": user.email
    } for user in users]) 