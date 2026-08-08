"""评论接口。"""
from fastapi import APIRouter, Query

from app.api.deps import CurrentAdmin, CurrentUser
from app.schemas.comment import (
    CommentCreate,
    CommentListResult,
    CommentOut,
    CommentStatusUpdate,
)
from app.schemas.common import ApiResponse
from app.services import comment_service

router = APIRouter(prefix="/comments", tags=["评论"])


@router.get(
    "/by-article",
    response_model=ApiResponse[list[CommentOut]],
    summary="按文章获取已通过评论（前台）",
)
async def list_by_article(article_id: int = Query(..., description="文章 id")) -> dict:
    data = await comment_service.list_by_article(article_id)
    return {"data": data}


@router.post("", response_model=ApiResponse[CommentOut], summary="提交评论（需登录，默认待审核）")
async def create_comment(payload: CommentCreate, user: CurrentUser) -> dict:
    data = await comment_service.create_comment(payload, user)
    return {"data": data}


@router.get("", response_model=ApiResponse[CommentListResult], summary="评论列表（管理员）")
async def list_comments(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: int | None = Query(None, ge=0, le=2, description="按状态过滤"),
    _: CurrentAdmin = None,
) -> dict:
    data = await comment_service.list_all(page=page, page_size=page_size, status=status)
    return {"data": data}


@router.put(
    "/{comment_id}/status",
    response_model=ApiResponse[CommentOut],
    summary="审核评论（管理员）",
)
async def update_status(comment_id: int, payload: CommentStatusUpdate, _: CurrentAdmin = None) -> dict:
    data = await comment_service.update_status(comment_id, payload.status)
    return {"data": data}


@router.delete("/{comment_id}", response_model=ApiResponse, summary="删除评论（管理员）")
async def delete_comment(comment_id: int, _: CurrentAdmin = None) -> dict:
    await comment_service.delete_comment(comment_id)
    return {"message": "删除成功"}
