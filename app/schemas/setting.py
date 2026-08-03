"""站点设置 Schema。"""
from pydantic import BaseModel, ConfigDict


class SettingOut(BaseModel):
    """设置出参。"""

    key: str
    value: str

    model_config = ConfigDict(from_attributes=True)
