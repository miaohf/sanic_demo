from tortoise.models import Model
from tortoise import fields

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=200)
    email = fields.CharField(max_length=120)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "users" 