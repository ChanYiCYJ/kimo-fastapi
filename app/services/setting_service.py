"""站点设置业务。"""
from app.crud.setting import setting as setting_crud


async def get_all_settings() -> dict:
    """返回键值对字典。"""
    rows = await setting_crud.get_multi(limit=200)
    return {row.key: row.value for row in rows}


async def get_setting(key: str) -> str | None:
    obj = await setting_crud.get_by_key(key)
    return obj.value if obj else None


async def set_setting(key: str, value: str) -> dict:
    obj = await setting_crud.set_value(key, value)
    return {"key": obj.key, "value": obj.value}


async def delete_setting(key: str) -> None:
    await setting_crud.remove_by_key(key)
