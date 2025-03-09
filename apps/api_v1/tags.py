from sanic.views import HTTPMethodView
from sanic.response import json
from sanic_ext import openapi
from schemas.tag import TagCreate, TagResponse
from models.tag import Tag
from middleware.jwt_middleware import jwt_required
from tortoise.exceptions import DoesNotExist, IntegrityError

class TagView(HTTPMethodView):
    @openapi.summary("获取标签列表")
    async def get(self, request):
        tags = await Tag.all()
        return json({
            "tags": [{
                "id": tag.id,
                "name": tag.name
            } for tag in tags]
        })
    
    @openapi.summary("创建新标签")
    @openapi.body({"name": str})
    @openapi.response(201, {"id": int, "name": str})
    async def post(self, request):
        try:
            data = request.json
            
            # 验证数据
            if not data.get('name'):
                return json({"error": "标签名称不能为空"}, status=400)
            
            # 检查标签是否已存在
            existing_tag = await Tag.filter(name=data['name']).first()
            if existing_tag:
                return json({"error": "标签已存在"}, status=400)
            
            # 创建新标签
            tag = await Tag.create(name=data['name'])
            
            return json({
                "id": tag.id,
                "name": tag.name
            }, status=201)
            
        except Exception as e:
            return json({"error": f"创建标签失败: {str(e)}"}, status=500)

class TagDetailView(HTTPMethodView):
    @openapi.summary("获取标签详情")
    async def get(self, request, tag_id):
        tag = await Tag.get_or_none(id=tag_id)
        if not tag:
            return json({"error": "标签不存在"}, status=404)
            
        # 获取与该标签相关的帖子
        await tag.fetch_related("posts")
        
        return json({
            "id": tag.id,
            "name": tag.name,
            "posts": [{
                "id": post.id,
                "title": post.title
            } for post in tag.posts]
        })
        
    @openapi.summary("更新标签")
    async def put(self, request, tag_id):
        tag = await Tag.get_or_none(id=tag_id)
        if not tag:
            return json({"error": "标签不存在"}, status=404)
            
        data = request.json
        if not data.get('name'):
            return json({"error": "标签名称不能为空"}, status=400)
            
        # 检查新名称是否已存在
        if data['name'] != tag.name:
            existing_tag = await Tag.filter(name=data['name']).first()
            if existing_tag:
                return json({"error": "标签名称已存在"}, status=400)
                
        # 更新标签
        tag.name = data['name']
        await tag.save()
        
        return json({
            "id": tag.id,
            "name": tag.name
        })
        
    @openapi.summary("删除标签")
    async def delete(self, request, tag_id):
        tag = await Tag.get_or_none(id=tag_id)
        if not tag:
            return json({"error": "标签不存在"}, status=404)
            
        await tag.delete()
        return json({"message": "标签已删除"}) 