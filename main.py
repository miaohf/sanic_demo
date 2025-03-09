from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS
from tortoise.contrib.sanic import register_tortoise

# 导入蓝图
from apps.api_v1.routes import bp as v1_blueprint
from apps.api_v2.routes import bp as v2_blueprint
from apps.auth.routes import bp as auth_bp
from middleware.jwt_middleware import add_user_to_request

app = Sanic("MyApp")

# 配置
app.config.update({
    'DB_URL': 'sqlite:///db.sqlite3',
    'JWT_SECRET': 'your-very-secret-and-very-long-random-key-here',
    'JWT_ACCESS_TOKEN_EXPIRES': 60 * 30,  # 30分钟
    'JWT_REFRESH_TOKEN_EXPIRES': 60 * 60 * 24 * 30,  # 30天
    'API_VERSION': '1.0.0',
    'API_TITLE': 'My API',
    'API_DESCRIPTION': 'API Documentation'
})

# 替换原有的数据库初始化
register_tortoise(
    app,
    db_url='sqlite://db.sqlite3',
    modules={'models': ['models.user', 'models.post', 'models.tag']},
    generate_schemas=True
)

# 初始化 CORS
CORS(app)

# 添加自定义JWT中间件
@app.middleware('request')
async def jwt_middleware(request):
    return await add_user_to_request(request)

# 注册蓝图
app.blueprint(v1_blueprint)
app.blueprint(v2_blueprint)
app.blueprint(auth_bp)

# 启用 OpenAPI
app.ext.openapi.describe("My API", version="1.0.0")

@app.route("/")
async def root(request):
    return json({
        "name": "Sanic Demo API",
        "version": app.config.API_VERSION,
        "documentation": "/docs"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True) 