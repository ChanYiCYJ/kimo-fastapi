"""图片上传接口。"""
import os
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.deps import CurrentAdmin
from app.core.config import settings
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/upload", tags=["上传"])


@router.post("/image", response_model=ApiResponse, summary="上传图片（管理员）")
async def upload_image(file: UploadFile = File(...), admin: CurrentAdmin = None) -> dict:
    ext = ""
    if "." in (file.filename or ""):
        ext = file.filename.rsplit(".", 1)[-1].lower()
    allowed = settings.ALLOWED_UPLOAD_EXTS.split(",")
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="文件超过 5MB 限制")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid4().hex}.{ext}"
    path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(content)

    # 写入媒体库（便于后台媒体管理页浏览/删除；写入失败不阻塞上传）
    from app.models.media import Media

    try:
        await Media.create(
            filename=filename,
            original_name=file.filename,
            url=f"/static/uploads/{filename}",
            size=len(content),
            mime=file.content_type,
            uploader_id=admin.id if admin else None,
        )
    except Exception:
        pass

    return {"data": {"url": f"/static/uploads/{filename}", "filename": filename}}
