"""文章接口。"""
from fastapi import APIRouter, Query

from app.api.deps import CurrentAdmin
from app.schemas.article import ArticleCreate, ArticleListItem, ArticleOut, ArticleUpdate
from app.schemas.common import ApiResponse
from app.services import article_service

router = APIRouter(prefix="/articles", tags=["文章"])


@router.get("", response_model=ApiResponse, summary="文章列表（分页/筛选/搜索）")
async def list_articles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int | None = Query(None, ge=1, le=50, description="每页数量（默认 5）"),
    category_id: int | None = Query(None, description="按分类过滤"),
    keyword: str | None = Query(None, description="标题关键词"),
) -> dict:
    data = await article_service.list_articles(
        page=page, category_id=category_id, keyword=keyword, page_size=page_size
    )
    return {"data": data}


@router.get("/search", response_model=ApiResponse[list[ArticleListItem]], summary="搜索文章")
async def search_articles(keyword: str = Query(..., min_length=1, description="关键词")) -> dict:
    items = await article_service.search(keyword)
    return {"data": items}


@router.get("/{article_id}", response_model=ApiResponse[ArticleOut], summary="文章详情")
async def get_article(article_id: int) -> dict:
    data = await article_service.get_article(article_id)
    return {"data": data}


@router.post("", response_model=ApiResponse[ArticleOut], summary="创建文章（管理员）")
async def create_article(payload: ArticleCreate, _: CurrentAdmin) -> dict:
    data = await article_service.create_article(payload)
    return {"data": data}


@router.put("/{article_id}", response_model=ApiResponse[ArticleOut], summary="更新文章（管理员）")
async def update_article(article_id: int, payload: ArticleUpdate, _: CurrentAdmin) -> dict:
    data = await article_service.update_article(article_id, payload)
    return {"data": data}


@router.delete("/{article_id}", response_model=ApiResponse, summary="删除文章（管理员）")
async def delete_article(article_id: int, _: CurrentAdmin) -> dict:
    await article_service.delete_article(article_id)
    return {"message": "删除成功"}
