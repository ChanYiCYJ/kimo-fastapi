"""Markdown → HTML 渲染（与 Kimo 原项目一致）。"""
import markdown

_MARKDOWN_EXTENSIONS = [
    "tables",
    "toc",
    "fenced_code",
    "pymdownx.superfences",
    "pymdownx.tasklist",
    "pymdownx.details",
    "pymdownx.inlinehilite",
]


def markdown_to_html(content: str) -> str:
    """将 Markdown 文本渲染为 HTML。"""
    if not content:
        return ""
    return markdown.markdown(content, extensions=_MARKDOWN_EXTENSIONS)
