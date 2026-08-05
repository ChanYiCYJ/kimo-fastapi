"""网络搜索 / 网页抓取代理（海外服务器可直接访问 Bing/DDG/Wikipedia）。

前端 Cloudflare Worker 在部分地区（如 HKG）无法直连这些搜索源，
通过本端点在海外转发，解决 CORS 与地域限制。
"""
import re
from typing import Any
from urllib.parse import unquote

import httpx
from fastapi import APIRouter, Query

from app.schemas.common import ApiResponse

router = APIRouter(tags=["搜索"])

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

HEADERS = {"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def _host(url: str) -> str:
    try:
        return httpx.URL(url).host or ""
    except Exception:
        return ""


async def _search_bing(client: httpx.AsyncClient, query: str, limit: int) -> list[dict]:
    res = await client.get(
        "https://www.bing.com/search",
        params={"q": query, "count": min(20, limit)},
    )
    if res.status_code != 200:
        return []
    html = res.text
    out: list[dict] = []
    seen: set[str] = set()
    # Bing 结果块：新版为 <li class="b_algo ...">，旧版 <li class="b_algo">
    for block in re.findall(r'<li class="b_algo[^"]*"[\s\S]*?</li>', html):
        if len(out) >= limit:
            break
        href = re.search(r'<h2[^>]*>\s*<a[^>]*href="([^"]+)"', block)
        title = re.search(
            r'<h2[^>]*>\s*<a[^>]*href="[^"]*"[^>]*>([\s\S]*?)</a>', block
        )
        snip = re.search(r'<p[^>]*class="b_lineclamp[^"]*"[^>]*>([\s\S]*?)</p>', block)
        if href and title:
            url = href.group(1)
            t = _norm(re.sub(r"<[^>]+>", "", title.group(1)))
            d = _norm(re.sub(r"<[^>]+>", "", snip.group(1))) if snip else ""
            if t and url and url not in seen:
                seen.add(url)
                out.append(
                    {"title": t, "url": url, "description": d, "source": _host(url), "engine": "bing"}
                )
    return out


async def _search_ddg(client: httpx.AsyncClient, query: str, limit: int) -> list[dict]:
    res = await client.get("https://html.duckduckgo.com/html/", params={"q": query})
    if res.status_code != 200:
        return []
    html = res.text
    links = list(
        re.finditer(r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([\s\S]*?)</a>', html)
    )
    snips = list(re.finditer(r'<a[^>]*class="result__snippet"[^>]*>([\s\S]*?)</a>', html))
    out: list[dict] = []
    seen: set[str] = set()
    for i, m in enumerate(links):
        if len(out) >= limit:
            break
        raw = m.group(1) or ""
        target = raw
        # DDG 结果常为 //duckduckgo.com/l/?uddg=<encoded> 跳转形式
        um = re.search(r"[?&]uddg=([^&]+)", raw)
        if um:
            target = unquote(um.group(1))
        elif raw.startswith("http"):
            target = raw
        t = _norm(re.sub(r"<[^>]+>", "", m.group(2)))
        d = _norm(re.sub(r"<[^>]+>", "", snips[i].group(1))) if i < len(snips) else ""
        if t and target and target not in seen:
            seen.add(target)
            out.append(
                {"title": t, "url": target, "description": d, "source": _host(target), "engine": "duckduckgo"}
            )
    return out


async def _search_wiki(client: httpx.AsyncClient, query: str, limit: int) -> list[dict]:
    res = await client.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "opensearch",
            "format": "json",
            "limit": limit,
            "namespace": 0,
            "search": query,
        },
    )
    if res.status_code != 200:
        return []
    d = res.json()
    titles = [t for t in (d[1] or []) if t]
    descs = d[2] or []
    urls = d[3] or []
    return [
        {
            "title": titles[i],
            "url": urls[i] or "",
            "description": _norm(descs[i]) if i < len(descs) else "",
            "source": "wikipedia.org",
            "engine": "wikipedia",
        }
        for i in range(len(titles))
    ]


@router.get("/search", response_model=ApiResponse[list[dict]], summary="多引擎网络搜索")
async def search(
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(8, ge=1, le=20),
    engines: str = Query("bing,duckduckgo,wikipedia", description="逗号分隔引擎"),
) -> dict:
    engine_list = [e.strip() for e in engines.split(",") if e.strip()]
    out: list[dict] = []
    seen: set[str] = set()
    async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
        for engine in engine_list:
            if len(out) >= limit:
                break
            try:
                if engine == "bing":
                    items = await _search_bing(client, q, limit - len(out))
                elif engine == "duckduckgo":
                    items = await _search_ddg(client, q, limit - len(out))
                elif engine == "wikipedia":
                    items = await _search_wiki(client, q, limit - len(out))
                else:
                    continue
                for item in items:
                    if item.get("url") and item["url"] not in seen and len(out) < limit:
                        seen.add(item["url"])
                        out.append(item)
            except Exception:
                continue
    return {"data": out}


@router.get("/fetch", response_model=ApiResponse[dict], summary="网页抓取（含 og:image）")
async def fetch_web(
    url: str = Query(..., description="目标 URL"),
    max_chars: int = Query(30000, ge=500, le=200000),
) -> dict:
    if not re.match(r"^https?://", url):
        return {"data": {"error": "Invalid URL"}}
    async with httpx.AsyncClient(headers=HEADERS, timeout=20, follow_redirects=True) as client:
        res = await client.get(url)
    if res.status_code != 200:
        return {"data": {"error": f"HTTP {res.status_code}"}}
    ct = res.headers.get("content-type", "text/plain")
    raw = res.text
    final_url = str(res.url)
    title = ""
    image = ""
    text = raw
    if "text/html" in ct or "<html" in raw:
        tm = re.search(r"<title[^>]*>([\s\S]*?)</title>", raw, re.I)
        title = _norm(tm.group(1)) if tm else ""
        im = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', raw, re.I)
        if not im:
            im = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']', raw, re.I)
        image = im.group(1).strip() if im else ""
        text = (
            raw.replace("<script", " <script")
            .replace("<style", " <style")
            .replace("<script", " <script")
        )
        text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
        text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
    text = text.strip()
    truncated = len(text) > max_chars
    content = text[:max_chars]
    return {
        "data": {
            "url": url,
            "finalUrl": final_url,
            "contentType": ct,
            "title": title,
            "image": image,
            "retrievalMethod": "proxy",
            "truncated": truncated,
            "content": content,
        }
    }
