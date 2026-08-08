"""站点统计业务（纯 SQL 聚合，不建表）。"""
from datetime import datetime, timedelta

from tortoise import Tortoise

from app.models.article import Article
from app.models.category import Category
from app.models.page import Page
from app.models.tag import Tag
from app.models.user import UserInfo

TREND_DAYS = 14


async def get_overview() -> dict:
    """站点概览统计：内容计数 + 近 {TREND_DAYS} 天发文趋势 + 分类分布。"""
    total_articles = await Article.all().count()
    total_categories = await Category.all().count()
    total_tags = await Tag.all().count()
    total_pages = await Page.all().count()
    total_users = await UserInfo.all().count()

    conn = Tortoise.get_connection("default")
    start = datetime.now() - timedelta(days=TREND_DAYS - 1)
    start_str = start.strftime("%Y-%m-%d")

    # 近 14 天按日发文数
    _, trend_rows = await conn.execute_query(
        "SELECT DATE(created) AS d, COUNT(*) AS c "
        "FROM articles WHERE created >= %s GROUP BY DATE(created) ORDER BY d",
        [start_str],
    )
    trend_map: dict[str, int] = {str(r["d"]): r["c"] for r in trend_rows}

    # 分类分布（含未分类）
    _, dist_rows = await conn.execute_query(
        "SELECT COALESCE(c.name, '未分类') AS name, COUNT(*) AS c "
        "FROM articles a LEFT JOIN categories c ON a.category_id = c.id "
        "GROUP BY a.category_id ORDER BY c DESC",
    )
    category_distribution = [
        {"name": r["name"], "count": r["c"]} for r in dist_rows
    ]

    # 生成完整日期序列（无文章的天补 0）
    trend: list[dict] = []
    for i in range(TREND_DAYS):
        day = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        trend.append({"date": day, "count": trend_map.get(day, 0)})

    return {
        "articles": total_articles,
        "categories": total_categories,
        "tags": total_tags,
        "pages": total_pages,
        "users": total_users,
        "trend": trend,
        "category_distribution": category_distribution,
    }
