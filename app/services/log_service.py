"""操作日志业务。"""
import math

from app.crud.log import log as log_crud


async def list_logs(
    page: int = 1, page_size: int = 20, action: str | None = None
) -> dict:
    items = await log_crud.get_multi_page(page=page, page_size=page_size, action=action)
    total = await log_crud.count(action=action)
    total_page = max(1, math.ceil(total / page_size))
    return {
        "items": [
            {
                "id": r.id,
                "created": r.created,
                "user_id": r.user_id,
                "username": r.username,
                "action": r.action,
                "method": r.method,
                "path": r.path,
                "status": r.status,
                "ms": r.ms,
                "ip": r.ip,
            }
            for r in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_page": total_page,
    }
