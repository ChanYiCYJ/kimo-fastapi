"""用户业务（管理员管理用户）。"""
from fastapi import HTTPException

from app.crud.user import user as user_crud


def _to_out(user) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "user_name": user.user_name,
        "role": user.role,
    }


async def list_users() -> list:
    """用户列表（全部，最多 500）。"""
    return [_to_out(u) for u in await user_crud.get_multi(limit=500)]


async def set_role(user_id: int, role: int, operator) -> dict:
    """设置用户角色。"""
    obj = await user_crud.get(user_id)
    if not obj:
        raise HTTPException(status_code=404, detail="用户不存在")
    if obj.id == operator.id:
        raise HTTPException(status_code=400, detail="不能修改自己的权限")
    obj = await user_crud.update(obj, {"role": role})
    return _to_out(obj)


async def delete_user(user_id: int, operator) -> None:
    """删除用户。"""
    if user_id == operator.id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    obj = await user_crud.get(user_id)
    if not obj:
        raise HTTPException(status_code=404, detail="用户不存在")
    await user_crud.remove(user_id)
