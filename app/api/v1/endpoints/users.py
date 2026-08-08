"""用户管理接口（管理员）。"""
from fastapi import APIRouter

from app.api.deps import CurrentAdmin
from app.schemas.auth import UserOut
from app.schemas.common import ApiResponse
from app.schemas.user import UserRoleUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("", response_model=ApiResponse[list[UserOut]], summary="用户列表（管理员）")
async def list_users(_: CurrentAdmin) -> dict:
    data = await user_service.list_users()
    return {"data": data}


@router.put(
    "/{user_id}/role",
    response_model=ApiResponse[UserOut],
    summary="设置用户角色（管理员）",
)
async def set_user_role(user_id: int, payload: UserRoleUpdate, admin: CurrentAdmin) -> dict:
    data = await user_service.set_role(user_id, payload.role, admin)
    return {"data": data}


@router.delete("/{user_id}", response_model=ApiResponse, summary="删除用户（管理员）")
async def delete_user(user_id: int, admin: CurrentAdmin) -> dict:
    await user_service.delete_user(user_id, admin)
    return {"message": "删除成功"}
