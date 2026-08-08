"""系统操作日志接口（管理员）。"""
from fastapi import APIRouter, Query

from app.api.deps import CurrentAdmin
from app.schemas.common import ApiResponse
from app.schemas.log import LogListResult
from app.services import log_service

router = APIRouter(prefix="/logs", tags=["日志"])


@router.get("", response_model=ApiResponse[LogListResult], summary="操作日志（管理员）")
async def list_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    action: str | None = Query(None, description="按操作类型过滤（CREATE/UPDATE/DELETE）"),
    _: CurrentAdmin = None,
) -> dict:
    data = await log_service.list_logs(page=page, page_size=page_size, action=action)
    return {"data": data}
