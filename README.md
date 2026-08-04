<div align="center">

# Kimo API

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)
![Tortoise ORM](https://img.shields.io/badge/Tortoise%20ORM-0.22+-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

**一个轻量级博客后端 API · 由 [Kimo](https://github.com/ChanYiCYJ/Kimo)（Flask）重构而来**

</div>

---

## ✨ 项目简介

将 [Kimo](https://github.com/ChanYiCYJ/Kimo)（Flask 博客系统）重构为 **FastAPI + Tortoise ORM 的纯 JSON API 后端**。

- 完全兼容原数据库：直接对接 `userinfo / articles / categories / tags / article_tags / page / setting` 表，历史数据直接可用
- 认证升级为 **JWT**（原 Session），密码哈希沿用 `werkzeug`，旧账号可直接登录
- 纯 API（前后端分离），自带 Swagger 文档
- 分层架构：`core → models → schemas → crud → services → api`

## 🎯 功能特性

- ✅ 文章管理：发布、浏览、编辑、删除，支持 Markdown 渲染与封面图
- ✅ 分类 / 标签：分类 slug 自动拼音，标签自动创建与关联
- ✅ 用户认证：注册 / 登录（JWT），管理员（role=0）权限控制
- ✅ 自定义页面：支持 markdown / html / list / link 四种类型
- ✅ 站点设置：键值对配置管理
- ✅ 图片上传：UUID 命名、类型与大小校验
- ✅ 文章搜索：按标题关键词检索，分页查询

## � 默认管理员与开放注册

> **后端不会通过注册创建管理员**（注册接口一律生成 `role=1` 普通用户）。

首次启动时，若数据库中不存在任何管理员（`role=0`），后端会自动创建一个**默认管理员**：

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `AUTO_CREATE_ADMIN` | `True` | 是否自动创建初始管理员 |
| `ADMIN_USERNAME` | `admin` | 管理员用户名 |
| `ADMIN_EMAIL` | `admin@kimo.dev` | 管理员邮箱 |
| `ADMIN_PASSWORD` | `admin123` | 管理员密码 |

> ⚠️ **安全提醒**：默认密码仅为首次登录使用，**部署后务必通过环境变量修改 `ADMIN_PASSWORD`**，或登录后台后修改用户权限。

**开放注册**由以下两级控制（任一级设为关闭即拒绝注册）：

1. 站点设置 `allow_register`（后台「站点设置」写入 `0` = 关闭，优先级更高）
2. 环境变量 `ALLOW_REGISTER`（默认 `True`）

关闭注册后，`POST /api/v1/auth/register` 会返回 `403 当前站点未开放注册`。

## �🚀 快速开始

### 环境要求

- Python 3.10+
- MySQL 5.7+（或使用本地其他支持的数据库）

### 安装与启动

```bash
# 1. 克隆仓库
git clone <your-repo-url> && cd <repo-name>

# 2. 创建虚拟环境并安装依赖
python -m venv venv
source venv/bin/activate      # Linux / macOS
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env          # 修改数据库连接与 JWT 密钥

# 4. 启动服务
uvicorn app.main:app --reload
```

启动后访问 http://127.0.0.1:8000/docs 查看 Swagger 文档。

## 📁 目录结构

```
├── app/
│   ├── main.py                  # FastAPI 入口（lifespan 初始化 DB + 静态目录）
│   ├── core/
│   │   ├── config.py            # pydantic-settings 配置（读 .env）
│   │   ├── database.py          # TORTOISE_ORM（aerich 引用）与连接初始化
│   │   └── security.py          # JWT 令牌 + werkzeug 密码哈希
│   ├── models/                  # Tortoise 模型（映射 7 张表）
│   │   ├── user.py              #   userinfo
│   │   ├── article.py           #   articles
│   │   ├── category.py          #   categories
│   │   ├── tag.py               #   tags
│   │   ├── article_tag.py       #   article_tags（复合主键，只读模型）
│   │   ├── page.py              #   page
│   │   └── setting.py           #   setting（主键为 key）
│   ├── schemas/                 # Pydantic 校验模型（含统一响应 ApiResponse）
│   ├── crud/                    # 单表数据访问（通用基类 + 各资源）
│   ├── services/                # 业务层：认证 / 文章 / 分类 / 标签 / 页面 / 设置
│   ├── utils/                   # markdown 渲染、中文拼音 slug
│   └── api/
│       ├── deps.py              # JWT 依赖：CurrentUser / CurrentAdmin(role=0)
│       └── v1/endpoints/        # auth / articles / categories / tags / pages / settings / upload
├── tests/                       # 接口冒烟测试（pytest）
├── static/uploads/              # 图片上传目录（不入库）
├── migrations/                  # aerich 迁移目录
├── .env.example                 # 环境变量示例
├── pyproject.toml               # 依赖 + aerich 配置
└── requirements.txt
```

## 🔌 接口一览（前缀 /api/v1）

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| POST | `/auth/register` | 注册普通用户 | 公开 |
| POST | `/auth/login` | 登录（用户名/邮箱），返回 JWT | 公开 |
| GET | `/auth/me` | 当前登录用户 | 登录 |
| GET | `/articles?page=&category_id=&keyword=` | 文章列表（分页/筛选/搜索） | 公开 |
| GET | `/articles/search?keyword=` | 标题搜索 | 公开 |
| GET | `/articles/{id}` | 文章详情（含 content_html） | 公开 |
| POST | `/articles` | 创建文章（含分类/标签） | 管理员 |
| PUT | `/articles/{id}` | 更新文章 | 管理员 |
| DELETE | `/articles/{id}` | 删除文章 | 管理员 |
| GET | `/categories` | 分类列表 | 公开 |
| POST | `/categories` | 创建分类（slug 自动拼音） | 管理员 |
| GET | `/tags` | 标签列表 | 公开 |
| POST | `/tags` | 创建标签 | 管理员 |
| GET | `/pages` | 页面列表 | 公开 |
| GET | `/pages/by-name/{name}` | 按名称取页面（Markdown 自动渲染） | 公开 |
| GET | `/pages/{id}` | 页面详情 | 公开 |
| POST/PUT/DELETE | `/pages...` | 页面管理 | 管理员 |
| GET | `/settings` | 全部站点设置 | 公开 |
| PUT | `/settings/{key}` | 写入设置 | 管理员 |
| POST | `/upload/image` | 图片上传 | 管理员 |

> 登录返回 `access_token`，后续请求在 `Authorization: Bearer <token>` 头中携带。
> 管理员 = `userinfo.role = 0`（Kimo 原项目约定）。

## 🔄 与 Kimo 原项目的差异（优化点）

| 维度 | Kimo（Flask） | 本重构（FastAPI） |
| --- | --- | --- |
| 认证 | Session | JWT（无状态、可跨端） |
| 数据访问 | 手写 SQL（DBUtils） | Tortoise ORM + 原生 JOIN 处理复合主键 |
| 接口 | 模板渲染 + JSON 混合 | 纯 JSON + 统一响应格式 + OpenAPI 文档 |
| 校验 | 手工校验 | Pydantic 自动校验 |
| 配置 | config.json 全局文件 | .env + pydantic-settings |
| 迁移 | 手写 SQL 脚本 | aerich 迁移（可增量） |
| 测试 | 无 | pytest 接口测试 |

## 🧪 测试

```bash
python -m pytest tests -v
```

测试使用 `e2e_` 前缀的临时数据并自动清理，不影响真实数据。

## 🛠 常用命令

```bash
# 启动开发服务
uvicorn app.main:app --reload

# 运行测试
python -m pytest tests -v

# 模型变更后生成迁移（表结构由迁移管理，勿用 generate_schemas）
aerich init -t app.core.database.TORTOISE_ORM   # 首次
aerich migrate && aerich upgrade
```

## 📄 License

本项目基于 [MIT License](LICENSE) 开源。

---

Made with ❤️ 基于 [Kimo](https://github.com/ChanYiCYJ/Kimo) 重构
