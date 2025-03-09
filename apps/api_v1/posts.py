from sanic.views import HTTPMethodView
from sanic.response import json
from sanic_ext import openapi
from schemas.post import PostCreate, PostResponse, PostUpdate
from models.post import Post
from models.tag import Tag
from middleware.jwt_middleware import jwt_required
from tortoise.exceptions import DoesNotExist

class PostView(HTTPMethodView):
    @openapi.summary("获取帖子列表")
    async def get(self, request):
        posts = await Post.all().prefetch_related('user', 'tags')
        
        return json({
            "posts": [{
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "created_at": str(post.created_at),
                "user": {
                    "id": post.user.id,
                    "username": post.user.username
                },
                "tags": [{
                    "id": tag.id,
                    "name": tag.name
                } for tag in post.tags]
            } for post in posts]
        })
        
    @openapi.summary("创建新帖子")
    @openapi.body({
        "title": str,
        "content": str,
        "tag_ids": [int]
    })
    async def post(self, request):
        try:
            data = request.json
            
            # 验证数据
            if not data.get('title') or not data.get('content'):
                return json({"error": "标题和内容不能为空"}, status=400)
            
            # 创建帖子
            post = await Post.create(
                title=data['title'],
                content=data['content'],
                user_id=request.ctx.user.id  # 从JWT中获取的用户
            )
            
            # 添加标签
            if data.get('tag_ids'):
                tags = await Tag.filter(id__in=data['tag_ids'])
                await post.tags.add(*tags)
            
            # 重新获取帖子（包含关联数据）
            post = await Post.get(id=post.id).prefetch_related('user', 'tags')
            
            return json({
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "created_at": str(post.created_at),
                "user": {
                    "id": post.user.id,
                    "username": post.user.username
                },
                "tags": [{
                    "id": tag.id,
                    "name": tag.name
                } for tag in post.tags]
            }, status=201)
            
        except Exception as e:
            return json({"error": f"创建帖子失败: {str(e)}"}, status=500)

class PostDetailView(HTTPMethodView):
    @openapi.summary("获取帖子详情")
    async def get(self, request, post_id):
        post = await Post.get_or_none(id=post_id).prefetch_related('user', 'tags')
        if not post:
            return json({"error": "帖子不存在"}, status=404)
            
        return json({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": str(post.created_at),
            "user": {
                "id": post.user.id,
                "username": post.user.username
            },
            "tags": [{
                "id": tag.id,
                "name": tag.name
            } for tag in post.tags]
        })
        
    @openapi.summary("更新帖子")
    async def put(self, request, post_id):
        post = await Post.get_or_none(id=post_id)
        if not post:
            return json({"error": "帖子不存在"}, status=404)
            
        # 检查权限（只有作者可以更新）
        if post.user_id != request.ctx.user.id:
            return json({"error": "没有权限修改此帖子"}, status=403)
            
        data = request.json
        if not data.get('title') or not data.get('content'):
            return json({"error": "标题和内容不能为空"}, status=400)
            
        # 更新帖子
        post.title = data.get('title')
        post.content = data.get('content')
        await post.save()
        
        # 更新标签
        if data.get('tag_ids'):
            # 清除现有标签关联
            await post.tags.clear()
            # 添加新标签
            tags = await Tag.filter(id__in=data['tag_ids'])
            await post.tags.add(*tags)
        
        # 获取更新后的帖子
        post = await Post.get(id=post.id).prefetch_related('user', 'tags')
        
        return json({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "updated_at": str(post.updated_at),
            "user": {
                "id": post.user.id,
                "username": post.user.username
            },
            "tags": [{
                "id": tag.id,
                "name": tag.name
            } for tag in post.tags]
        })
        
    @openapi.summary("删除帖子")
    async def delete(self, request, post_id):
        post = await Post.get_or_none(id=post_id)
        if not post:
            return json({"error": "帖子不存在"}, status=404)
            
        # 检查权限（只有作者可以删除）
        if post.user_id != request.ctx.user.id:
            return json({"error": "没有权限删除此帖子"}, status=403)
            
        await post.delete()
        return json({"message": "帖子已成功删除"}) 