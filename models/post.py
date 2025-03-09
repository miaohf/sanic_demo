from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

class Post(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # 关系定义 - 多对一
    user = fields.ForeignKeyField("models.User", related_name="posts")
    
    # 关系定义 - 多对多
    tags = fields.ManyToManyField("models.Tag", related_name="posts")
    
    class Meta:
        table = "posts"

# 使用Pydantic 2.x自动创建模型
# Post_Pydantic = pydantic_model_creator(
#     Post, 
#     name="Post"
# ) 

# post = await Post.get(id=1)
# post_data = await Post_Pydantic.from_tortoise_orm(post)
# return json(post_data.dict())