"""认证接口。"""
from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.auth import LoginIn, RegisterIn, TokenOut, UserOut
from app.schemas.common import ApiResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=ApiResponse[UserOut], summary="注册")
async def register(payload: RegisterIn) -> dict:
    user = await auth_service.register(
        username=payload.username, email=payload.email, password=payload.password
    )
    return {"data": user}


@router.post("/login", response_model=ApiResponse[TokenOut], summary="登录")
async def login(payload: LoginIn) -> dict:
    result = await auth_service.login(payload.user_info, payload.password)
    return {"data": result}


@router.get("/me", response_model=ApiResponse[UserOut], summary="当前用户")
async def me(current_user: CurrentUser) -> dict:
    return {
        "data": {
            "id": current_user.id,
            "email": current_user.email,
            "user_name": current_user.user_name,
            "role": current_user.role,
        }
    }
