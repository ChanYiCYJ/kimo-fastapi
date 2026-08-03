"""用户数据访问。"""
from app.crud.base import CRUDBase
from app.models.user import UserInfo


class CRUDUserInfo(CRUDBase[UserInfo]):
    """用户表操作。"""

    async def get_by_name_or_email(self, identifier: str) -> UserInfo | None:
        # 注意：user_name 无唯一约束，需用 first() 而非 get_or_none()
        user = await self.model.filter(user_name=identifier).first()
        if user:
            return user
        return await self.model.filter(email=identifier).first()

    async def get_by_username(self, username: str) -> UserInfo | None:
        return await self.model.filter(user_name=username).first()

    async def get_by_email(self, email: str) -> UserInfo | None:
        return await self.model.filter(email=email).first()


user = CRUDUserInfo(UserInfo)
