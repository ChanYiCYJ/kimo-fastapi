"""站点备份业务。"""
import os
import subprocess
from datetime import datetime

from fastapi import HTTPException

from app.core.config import settings

BACKUP_DIR = os.path.join("static", "backups")


def _ensure_dir() -> None:
    os.makedirs(BACKUP_DIR, exist_ok=True)


async def list_backups() -> list:
    """备份文件列表（按名称倒序）。"""
    _ensure_dir()
    files = []
    for name in os.listdir(BACKUP_DIR):
        path = os.path.join(BACKUP_DIR, name)
        if os.path.isfile(path):
            files.append(
                {
                    "name": name,
                    "size": os.path.getsize(path),
                    "created": datetime.fromtimestamp(os.path.getmtime(path)).isoformat(),
                }
            )
    files.sort(key=lambda f: f["name"], reverse=True)
    return files


async def create_backup() -> dict:
    """创建备份（MySQL 用 mysqldump；sqlite 直接复制 db 文件）。"""
    _ensure_dir()
    filename = f"backup-{datetime.now():%Y%m%d-%H%M%S}.sql"
    path = os.path.join(BACKUP_DIR, filename)
    try:
        if settings.DB_ENGINE == "mysql":
            cmd = [
                "mysqldump",
                f"--host={settings.DB_HOST}",
                f"--port={settings.DB_PORT}",
                f"--user={settings.DB_USER}",
                f"--password={settings.DB_PASSWORD}",
                "--single-transaction",
                settings.DB_NAME,
            ]
            with open(path, "wb") as f:
                subprocess.run(
                    cmd, stdout=f, stderr=subprocess.DEVNULL, timeout=180, check=True
                )
        else:
            src = "db.sqlite3"
            if not os.path.exists(src):
                raise HTTPException(status_code=500, detail="数据库文件不存在")
            with open(src, "rb") as f:
                content = f.read()
            with open(path, "wb") as f:
                f.write(content)
    except subprocess.TimeoutExpired as exc:
        if os.path.exists(path):
            os.remove(path)
        raise HTTPException(status_code=500, detail="备份超时") from exc
    except subprocess.CalledProcessError as exc:
        if os.path.exists(path):
            os.remove(path)
        raise HTTPException(status_code=500, detail="备份失败（mysqldump 执行出错）") from exc
    return {
        "name": filename,
        "size": os.path.getsize(path),
        "created": datetime.now().isoformat(),
    }


def resolve_backup_path(filename: str) -> str:
    """校验文件名并返回完整路径（防路径穿越）。"""
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="非法文件名")
    _ensure_dir()
    path = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="备份不存在")
    return path


async def delete_backup(filename: str) -> None:
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="非法文件名")
    path = resolve_backup_path(filename)
    os.remove(path)
