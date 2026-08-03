"""页面业务：CRUD + 按类型渲染内容。"""
import json

from fastapi import HTTPException

from app.crud.page import page as page_crud
from app.utils.markdown import markdown_to_html

SUPPORT_TYPES = {"markdown", "html", "list", "link"}


async def list_pages() -> list:
    return await page_crud.get_multi(limit=200)


def _render_content(page) -> str:
    """按页面类型渲染 content。"""
    if page.type == "markdown":
        return markdown_to_html(page.content)
    if page.type == "list":
        try:
            return json.loads(page.content)
        except (json.JSONDecodeError, TypeError):
            return []
    # html / link 原样返回
    return page.content


async def get_page(page_id: int) -> dict:
    page = await page_crud.get(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="页面不存在")
    data = {
        "id": page.id,
        "name": page.name,
        "type": page.type,
        "status": page.status,
        "content": _render_content(page),
    }
    return data


async def get_page_by_name(name: str) -> dict:
    """按名称获取页面（前台访问），自动渲染内容。"""
    page = await page_crud.get_by_name(name)
    if not page:
        raise HTTPException(status_code=404, detail="页面不存在")
    return {
        "id": page.id,
        "name": page.name,
        "type": page.type,
        "status": page.status,
        "content": _render_content(page),
    }


async def create_page(payload) -> dict:
    if await page_crud.get_by_name(payload.name):
        raise HTTPException(status_code=400, detail="页面名称已存在")
    page = await page_crud.create(
        {
            "name": payload.name,
            "content": payload.content,
            "type": payload.type,
            "status": payload.status,
        }
    )
    return {
        "id": page.id,
        "name": page.name,
        "content": page.content,
        "type": page.type,
        "status": page.status,
    }


async def update_page(page_id: int, payload) -> dict:
    page = await page_crud.get(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="页面不存在")
    await page.update_from_dict(payload.model_dump(exclude_unset=True)).save()
    return {
        "id": page.id,
        "name": page.name,
        "content": page.content,
        "type": page.type,
        "status": page.status,
    }


async def delete_page(page_id: int) -> None:
    page = await page_crud.get(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="页面不存在")
    await page_crud.remove(page_id)
