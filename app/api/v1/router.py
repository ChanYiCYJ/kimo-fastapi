"""v1 版本路由汇总：所有端点在这里统一挂载。"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    articles,
    auth,
    categories,
    pages,
    search,
    settings,
    tags,
    upload,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(articles.router)
api_router.include_router(categories.router)
api_router.include_router(tags.router)
api_router.include_router(pages.router)
api_router.include_router(settings.router)
api_router.include_router(upload.router)
api_router.include_router(search.router)
