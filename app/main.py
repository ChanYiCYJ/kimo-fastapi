"""FastAPI 应用入口。

启动方式（在 backend 目录下）：
    uvicorn app.main:app --reload
"""
import asyncio
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.security import decode_access_token
from app.crud.user import user as user_crud
from app.models.log import SysLog
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


async def _write_log(
    user_id, username, action, method, path, status, ms, ip
) -> None:
    """后台任务：写操作日志（失败不影响业务）。"""
    try:
        await SysLog.create(
            user_id=user_id,
            username=username,
            action=action,
            method=method,
            path=path,
            status=status,
            ms=ms,
            ip=ip,
        )
    except Exception:
        pass


@app.middleware("http")
async def log_write_actions(request: Request, call_next):
    """记录所有写操作（POST/PUT/DELETE/PATCH）到操作日志（sys_log）。

    写日志放到后台任务执行，避免阻塞业务响应。
    """
    start = time.time()
    response = await call_next(request)
    ms = int((time.time() - start) * 1000)
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        user_id = None
        username = None
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            try:
                payload = decode_access_token(auth[7:])
                uid = int(payload["sub"])
                u = await user_crud.get(uid)
                if u:
                    user_id = uid
                    username = u.user_name or u.email
            except Exception:
                pass
        action = {
            "POST": "CREATE",
            "PUT": "UPDATE",
            "DELETE": "DELETE",
            "PATCH": "UPDATE",
        }.get(request.method, "CREATE")
        asyncio.create_task(
            _write_log(
                user_id,
                username,
                action,
                request.method,
                str(request.url.path),
                response.status_code,
                ms,
                request.client.host if request.client else None,
            )
        )
    return response


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
