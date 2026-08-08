"""站点统计接口（管理员）。"""
from fastapi import APIRouter

from app.api.deps import CurrentAdmin
from app.schemas.common import ApiResponse
from app.services import stats_service

router = APIRouter(prefix="/stats", tags=["统计"])


@router.get("/overview", response_model=ApiResponse, summary="站点概览统计（管理员）")
async def get_overview(_: CurrentAdmin) -> dict:
    data = await stats_service.get_overview()
    return {"data": data}
