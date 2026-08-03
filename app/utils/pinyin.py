"""中文转拼音 slug（与 Kimo 原项目 utils/pinyin.py 一致）。"""
from pypinyin import lazy_pinyin


def translate(text: str) -> str:
    """将中文转为无空格拼音字符串，用于生成 slug。"""
    return "".join(lazy_pinyin(text))
