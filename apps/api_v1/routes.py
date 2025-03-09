from sanic import Blueprint
from sanic.response import json
from sanic_ext import openapi

# 导入各个视图类
from apps.api_v1.users import UserView, UserDetailView
from apps.api_v1.posts import PostView, PostDetailView
from apps.api_v1.tags import TagView, TagDetailView

# 创建单一蓝图
bp = Blueprint("api_v1", url_prefix="/api/v1")

# 注册所有路由
bp.add_route(UserView.as_view(), "/users")
bp.add_route(UserDetailView.as_view(), "/users/<user_id:int>")
bp.add_route(PostView.as_view(), "/posts")
bp.add_route(PostDetailView.as_view(), "/posts/<post_id:int>")
bp.add_route(TagView.as_view(), "/tags")
bp.add_route(TagDetailView.as_view(), "/tags/<tag_id:int>")

# API版本信息路由
@bp.get("/")
@openapi.summary("API 版本信息")
@openapi.description("返回 API 版本信息")
@openapi.response(200, {"version": str, "status": str})
async def index(request):
    return json({
        "version": "1.0.0",
        "status": "active"
    })