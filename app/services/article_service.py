"""文章业务：CRUD、标签关联、Markdown 渲染、分页、搜索。"""
import math

from fastapi import HTTPException, status
from tortoise import Tortoise

from app.crud.article import article as article_crud
from app.crud.category import category as category_crud
from app.crud.tag import tag as tag_crud
from app.models.article import Article
from app.utils.markdown import markdown_to_html


async def _replace_article_tags(article_id: int, tag_names: list[str]) -> None:
    """重建某篇文章的标签关联（先清空，再按名插入）。"""
    conn = Tortoise.get_connection("default")
    # 清空旧关联
    await conn.execute_query(
        "DELETE FROM article_tags WHERE article_id = %s", [article_id]
    )
    # 按标签名逐条插入（不存在则自动创建）
    for name in tag_names:
        name = name.strip()
        if not name:
            continue
        tag_obj = await tag_crud.get_or_create(name)
        await conn.execute_query(
            "INSERT IGNORE INTO article_tags (article_id, tag_id) VALUES (%s, %s)",
            [article_id, tag_obj.id],
        )


async def _load_tags_map(articles: list[Article]) -> dict[int, list[dict]]:
    """批量加载文章标签（原生 JOIN，避免 N+1）。"""
    if not articles:
        return {}
    ids = [a.id for a in articles]
    placeholders = ",".join(["%s"] * len(ids))
    conn = Tortoise.get_connection("default")
    _, rows = await conn.execute_query(
        "SELECT at.article_id AS article_id, t.id AS tag_id, t.tag_name AS tag_name "
        "FROM article_tags at JOIN tags t ON at.tag_id = t.id "
        f"WHERE at.article_id IN ({placeholders})",
        ids,
    )
    result: dict[int, list[dict]] = {i: [] for i in ids}
    for row in rows:
        result[row["article_id"]].append(
            {"id": row["tag_id"], "tag_name": row["tag_name"]}
        )
    return result


def _to_list_item(article: Article, tags: list[dict]) -> dict:
    """组装列表项（不含正文）。"""
    return {
        "id": article.id,
        "title": article.title,
        "description": article.description,
        "cover_image": article.cover_image,
        "created": article.created,
        "category_id": article.category_id,
        "category_name": article.category.name if article.category else None,
        "tags": tags,
    }


def _to_detail(article: Article, tags: list[dict]) -> dict:
    """组装详情（正文渲染为 HTML，同时保留原始 Markdown）。"""
    item = _to_list_item(article, tags)
    item["content"] = article.content
    item["content_html"] = markdown_to_html(article.content)
    return item


async def list_articles(
    page: int = 1,
    category_id: int | None = None,
    keyword: str | None = None,
    page_size: int | None = None,
) -> dict:
    """分页文章列表（page_size 可自定义，默认 5）。"""
    size = page_size or article_crud.PAGE_SIZE
    items = await article_crud.get_multi_page(
        page=page, category_id=category_id, keyword=keyword, page_size=size
    )
    total = await article_crud.count(category_id=category_id, keyword=keyword)
    total_page = max(1, math.ceil(total / size))
    tags_map = await _load_tags_map(items)
    return {
        "items": [_to_list_item(a, tags_map.get(a.id, [])) for a in items],
        "total": total,
        "page": page,
        "page_size": size,
        "total_page": total_page,
    }


async def get_article(article_id: int) -> dict:
    """文章详情。"""
    article = await article_crud.get(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    tags_map = await _load_tags_map([article])
    return _to_detail(article, tags_map.get(article.id, []))


async def create_article(payload) -> dict:
    """创建文章。"""
    if payload.category_id is not None:
        if not await category_crud.get(payload.category_id):
            raise HTTPException(status_code=400, detail="分类不存在")

    article = await article_crud.create(
        {
            "title": payload.title,
            "content": payload.content,
            "description": payload.description,
            "cover_image": payload.cover_image,
            "category_id": payload.category_id,
        }
    )
    if payload.tags:
        await _replace_article_tags(article.id, payload.tags)
    # 重新加载分类并取标签
    article = await article_crud.get(article.id)
    tags_map = await _load_tags_map([article])
    return _to_detail(article, tags_map.get(article.id, []))


async def update_article(article_id: int, payload) -> dict:
    """更新文章。"""
    article = await article_crud.get(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    data = payload.model_dump(exclude_unset=True, exclude={"tags"})
    if "category_id" in data and data["category_id"] is not None:
        if not await category_crud.get(data["category_id"]):
            raise HTTPException(status_code=400, detail="分类不存在")

    if data:
        await article.update_from_dict(data).save()

    if payload.tags is not None:
        await _replace_article_tags(article_id, payload.tags)

    article = await article_crud.get(article_id)
    tags_map = await _load_tags_map([article])
    return _to_detail(article, tags_map.get(article.id, []))


async def delete_article(article_id: int) -> None:
    """删除文章（关联表由外键 CASCADE 自动清理）。"""
    article = await article_crud.get(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    await article_crud.remove(article_id)


async def search(keyword: str) -> list[dict]:
    """按标题关键词搜索文章。"""
    items = await article_crud.get_multi_page(page=1, keyword=keyword)
    tags_map = await _load_tags_map(items)
    return [_to_list_item(a, tags_map.get(a.id, [])) for a in items]
