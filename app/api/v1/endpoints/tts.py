"""文本转语音（TTS）—— edge-tts（微软 Edge 免费神经语音，无需 API key）。

前端「音频 TTS」设置地址填：
    https://<API 域名>/api/v1/tts?text={text}&voice=zh-CN-XiaoxiaoNeural
返回 audio/mpeg 并带 CORS 头，供前端 Web Audio 波形驱动 Live2D 口型（真实音频口型同步）。
"""
from fastapi import APIRouter, Query
from fastapi.responses import Response

router = APIRouter(tags=["TTS"])

# 常用免费中文神经语音（edge-tts 免费音色；完整列表见微软/edge-tts 文档）
TTS_VOICES: dict[str, str] = {
    "zh-CN-XiaoxiaoNeural": "晓晓 · 女声（温柔，最常用）",
    "zh-CN-YunxiNeural": "云希 · 男声",
    "zh-CN-XiaoyiNeural": "晓伊 · 女声（活泼）",
    "zh-CN-YunjianNeural": "云健 · 男声（浑厚）",
    "zh-CN-YunyangNeural": "云扬 · 男声（新闻）",
}


@router.get("/api/v1/tts")
async def text_to_speech(
    text: str = Query(..., min_length=1, max_length=2000, description="要朗读的文本"),
    voice: str = Query("zh-CN-XiaoxiaoNeural", description="edge-tts 语音（如 zh-CN-XiaoxiaoNeural）"),
    rate: str = Query("+0%", description="语速（如 +10% 加快 / -10% 放慢）"),
):
    if not text.strip():
        return Response(status_code=400, content="text 不能为空")

    # 懒加载：edge-tts 未安装时优雅降级，不影响其他端点
    try:
        import edge_tts
    except ImportError:
        return Response(
            status_code=503,
            content="服务器未安装 edge-tts（pip install edge-tts）",
        )

    try:
        chunks: list[bytes] = []
        communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                chunks.append(chunk["data"])
        mp3 = b"".join(chunks)
        if not mp3:
            return Response(status_code=502, content="TTS 生成失败（无音频输出）")
        return Response(
            mp3,
            media_type="audio/mpeg",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "public, max-age=3600",
            },
        )
    except Exception as e:  # noqa: BLE001
        return Response(status_code=502, content=f"TTS 生成失败：{e}")


@router.get("/api/v1/tts/voices")
async def tts_voices():
    """可用免费中文语音列表（方便前端展示）。"""
    return {"voices": TTS_VOICES}
