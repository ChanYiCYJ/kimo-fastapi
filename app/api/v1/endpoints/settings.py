"""站点设置接口。"""
from fastapi import APIRouter, Body

from app.api.deps import CurrentAdmin
from app.schemas.common import ApiResponse
from app.schemas.setting import SettingOut
from app.services import setting_service

router = APIRouter(prefix="/settings", tags=["站点设置"])


@router.get("", response_model=ApiResponse[dict], summary="全部设置")
async def get_settings() -> dict:
    data = await setting_service.get_all_settings()
    return {"data": data}


@router.put("/{key}", response_model=ApiResponse[SettingOut], summary="写入设置（管理员）")
async def set_setting(key: str, value: str = Body(..., embed=True), _: CurrentAdmin = None) -> dict:
    data = await setting_service.set_setting(key, value)
    return {"data": data}


@router.delete("/{key}", response_model=ApiResponse, summary="删除设置（管理员）")
async def delete_setting(key: str, _: CurrentAdmin) -> dict:
    await setting_service.delete_setting(key)
    return {"message": "删除成功"}
