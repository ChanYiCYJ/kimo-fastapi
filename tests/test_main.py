"""Kimo-FastAPI 重构版接口冒烟测试。

运行方式（在项目根目录下）：
    python -m pytest tests -v

注意：测试会连接项目的 MySQL 数据库，使用 e2e_ 前缀的临时数据并在结束时清理。
"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import close_db, init_db
from app.main import app

PREFIX = "e2e_"


@pytest.fixture
async def client():
    # ASGITransport 不执行 lifespan，手动初始化数据库
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    # 清理测试数据
    from tortoise import Tortoise

    db = Tortoise.get_connection("default")
    await db.execute_query(
        "DELETE FROM article_tags WHERE article_id IN (SELECT id FROM articles WHERE title LIKE %s)",
        ["e2e%"],
    )
    await db.execute_query("DELETE FROM articles WHERE title LIKE %s", ["e2e%"])
    await db.execute_query("DELETE FROM categories WHERE name LIKE %s", ["e2e%"])
    await db.execute_query("DELETE FROM tags WHERE tag_name LIKE %s", ["e2e%"])
    await db.execute_query("DELETE FROM page WHERE name LIKE %s", ["e2e%"])
    await db.execute_query("DELETE FROM setting WHERE `key` LIKE %s", ["e2e%"])
    await db.execute_query(
        "DELETE FROM userinfo WHERE user_name LIKE %s OR email LIKE %s",
        ["e2e_%", "e2e_%"],
    )
    await close_db()


@pytest.mark.anyio
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.anyio
async def test_unauthorized_admin_api(client):
    """未登录访问管理接口应 401。"""
    resp = await client.post(
        "/api/v1/articles", json={"title": "x", "content": "y"}
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_auth_flow(client):
    """注册 → 登录 → 获取当前用户。"""
    # 注册
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "e2e_user",
            "email": "e2e_user@example.com",
            "password": "secret123",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["role"] == 1

    # 登录
    resp = await client.post(
        "/api/v1/auth/login",
        json={"user_info": "e2e_user@example.com", "password": "secret123"},
    )
    assert resp.status_code == 200
    token = resp.json()["data"]["access_token"]

    # 获取当前用户
    resp = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["user_name"] == "e2e_user"

    # 错误密码
    resp = await client.post(
        "/api/v1/auth/login",
        json={"user_info": "e2e_user@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401
