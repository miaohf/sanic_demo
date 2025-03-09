# Sanic API 演示项目

这是一个使用 Sanic 框架构建的 RESTful API 演示项目，具有以下特点：

1. 使用 Pydantic 进行数据验证和序列化
2. 使用 Tortoise ORM 实现一对多和多对多关系模型
3. JWT 身份验证，支持 token 自动刷新
4. OpenAPI 文档自动生成

## 项目结构

```
sanic_demo/
├── apps/                 # API 路由模块
│   ├── api_v1/           # API v1 版本
│   │   ├── auth.py       # 身份验证 API
│   │   ├── posts.py      # 文章 API
│   │   ├── routes.py     # v1 路由主入口
│   │   ├── tags.py       # 标签 API
│   │   └── users.py      # 用户 API
│   └── api_v2/           # API v2 版本
├── middleware/           # 中间件
│   ├── auth.py           # 身份验证功能
│   └── jwt_middleware.py # JWT 中间件
├── models/               # 数据模型
│   ├── post.py           # 文章模型
│   ├── tag.py            # 标签模型
│   └── user.py           # 用户模型
├── schemas/              # 请求/响应模式
│   ├── post.py           # 文章相关模式
│   ├── tag.py            # 标签相关模式
│   └── user.py           # 用户相关模式
├── main.py               # 应用入口
└── requirements.txt      # 项目依赖
```

## 功能特点

1. **用户管理**
   - 用户注册与验证
   - 密码加密存储
   - JWT 身份验证

2. **关系模型**
   - 用户与文章的一对多关系
   - 文章与标签的多对多关系

3. **API 功能**
   - RESTful 设计
   - 基于 Pydantic 模型的数据验证
   - 自动序列化/反序列化

4. **安全特性**
   - JWT 访问令牌和刷新令牌
   - 令牌自动刷新机制
   - 基于权限的访问控制

## 安装和运行

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 运行应用：

```bash
python main.py
```

应用将在 `http://localhost:8000` 上运行，API 文档可在 `http://localhost:8000/docs` 访问。

## API 端点

### 身份验证

- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新令牌

### 用户

- `GET /api/v1/users` - 获取用户列表
- `POST /api/v1/users` - 创建新用户
- `GET /api/v1/users/{user_id}` - 获取用户详情

### 文章

- `GET /api/v1/posts` - 获取文章列表
- `POST /api/v1/posts` - 创建新文章
- `GET /api/v1/posts/{post_id}` - 获取文章详情
- `PUT /api/v1/posts/{post_id}` - 更新文章
- `DELETE /api/v1/posts/{post_id}` - 删除文章

### 标签

- `GET /api/v1/tags` - 获取标签列表
- `POST /api/v1/tags` - 创建新标签
- `GET /api/v1/tags/{tag_id}` - 获取标签详情
- `DELETE /api/v1/tags/{tag_id}` - 删除标签
