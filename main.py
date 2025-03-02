from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS
from sanic_jwt import Initialize
from sanic.blueprints import Blueprint
from sanic_ext import openapi
from tortoise.contrib.sanic import register_tortoise

from apps.api_v1.routes import bp as v1_blueprint
from apps.api_v2.routes import bp as v2_blueprint
# from models import db
from middleware.auth import authenticate

app = Sanic("MyApp")

# 配置
app.config.update({
    'DB_URL': 'sqlite:///db.sqlite3',
    'JWT_SECRET': 'your-very-secret-and-very-long-random-key-here',
    'API_VERSION': '1.0.0',
    'API_TITLE': 'My API',
    'API_DESCRIPTION': 'API Documentation'
})

# 替换原有的数据库初始化
register_tortoise(
    app,
    db_url='sqlite://db.sqlite3',
    modules={'models': ['models.user']},
    generate_schemas=True
)

# 初始化 CORS
CORS(app)

# 初始化 JWT
Initialize(
    app,
    authenticate=authenticate,
    url_prefix="/auth",
    path_to_authenticate="/login"
)

# 注册蓝图
app.blueprint(v1_blueprint)
app.blueprint(v2_blueprint)

# 启用 OpenAPI
app.ext.openapi.describe("My API", version="1.0.0")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True, single_process=True) 