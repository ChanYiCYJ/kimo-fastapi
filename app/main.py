"""FastAPI 应用入口。

启动方式（在 backend 目录下）：
    uvicorn app.main:app --reload
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import close_db, init_db
from app.services.init_service import ensure_default_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库、确保默认管理员，关闭时释放连接。"""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    await init_db()
    # 自动创建初始管理员（可经 AUTO_CREATE_ADMIN / ADMIN_* 配置，详见 config.py）
    await ensure_default_admin()
    yield
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Kimo 博客系统 · FastAPI + Tortoise ORM 重构版（纯 API + JWT）",
    lifespan=lifespan,
)

# 静态文件（上传的图片）
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount(
    "/static", StaticFiles(directory=settings.UPLOAD_DIR), name="static"
)

# 挂载 v1 版本路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["健康检查"], summary="服务状态")
async def root() -> dict:
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION, "status": "ok"}
