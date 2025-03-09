from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

class Tag(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)
    
    # 关系定义 - 多对多
    posts = fields.ManyToManyRelation["Post"]
    
    class Meta:
        table = "tags"

# # 使用Pydantic 2.x自动创建模型
# Tag_Pydantic = pydantic_model_creator(
#     Tag, 
#     name="Tag"
# ) 