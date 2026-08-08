"""站点备份接口（管理员）。"""
from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.api.deps import CurrentAdmin
from app.schemas.common import ApiResponse
from app.services import backup_service

router = APIRouter(prefix="/backups", tags=["备份"])


@router.get("", response_model=ApiResponse, summary="备份列表（管理员）")
async def list_backups(_: CurrentAdmin = None) -> dict:
    data = await backup_service.list_backups()
    return {"data": data}


@router.post("", response_model=ApiResponse, summary="创建备份（管理员）")
async def create_backup(_: CurrentAdmin = None) -> dict:
    data = await backup_service.create_backup()
    return {"data": data}


@router.get("/{filename}", summary="下载备份（管理员）")
async def download_backup(filename: str, _: CurrentAdmin = None):
    path = backup_service.resolve_backup_path(filename)
    return FileResponse(path, filename=filename)


@router.delete("/{filename}", response_model=ApiResponse, summary="删除备份（管理员）")
async def delete_backup(filename: str, _: CurrentAdmin = None) -> dict:
    await backup_service.delete_backup(filename)
    return {"message": "删除成功"}
