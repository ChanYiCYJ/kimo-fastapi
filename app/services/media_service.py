"""媒体库业务。"""
import math
import os

from fastapi import HTTPException

from app.core.config import settings
from app.crud.media import media as media_crud


async def list_media(
    page: int = 1, page_size: int = 24, mime_type: str | None = None
) -> dict:
    """分页媒体列表（倒序）。"""
    items = await media_crud.get_multi_page(
        page=page, page_size=page_size, mime_type=mime_type
    )
    total = await media_crud.count(mime_type=mime_type)
    total_page = max(1, math.ceil(total / page_size))
    return {
        "items": [
            {
                "id": m.id,
                "filename": m.filename,
                "original_name": m.original_name,
                "url": m.url,
                "size": m.size,
                "mime": m.mime,
                "created": m.created,
            }
            for m in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_page": total_page,
    }


async def delete_media(media_id: int) -> None:
    """删除媒体记录及其磁盘文件。"""
    obj = await media_crud.get(media_id)
    if not obj:
        raise HTTPException(status_code=404, detail="文件不存在")
    try:
        path = os.path.join(settings.UPLOAD_DIR, obj.filename)
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass  # 磁盘删除失败不阻塞记录删除
    await media_crud.remove(media_id)
