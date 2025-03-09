from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
import bcrypt

class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=128)
    email = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # 关系定义 - 一对多
    posts = fields.ReverseRelation["Post"]
    
    async def save(self, *args, **kwargs):
        # 如果是新用户或密码已更改，则对密码进行哈希处理
        if not self.id or self._saved_in_db is False:
            self.password = bcrypt.hashpw(
                self.password.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
        
        await super().save(*args, **kwargs)
    
    class Meta:
        table = "users"

# # 使用Pydantic 2.x创建模型
# User_Pydantic = pydantic_model_creator(
#     User, 
#     name="User",
#     exclude=("password",)
# ) 