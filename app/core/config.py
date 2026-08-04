"""应用配置。

使用 pydantic-settings 从 .env / 环境变量读取配置，
统一通过 `settings` 单例访问。
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置项。"""

    # ----- 应用 -----
    APP_NAME: str = "FastAPI 标准项目示例"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ----- 数据库 -----
    DB_ENGINE: str = "sqlite"  # 支持 mysql / sqlite
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "fastapi_demo"

    # ----- 数据库连接池（MySQL 时生效）-----
    DB_POOL_MAX_SIZE: int = 20
    DB_POOL_MIN_SIZE: int = 1
    DB_POOL_IDLE_TIMEOUT: int = 30

    # ----- JWT 认证 -----
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 默认 7 天

    # ----- 上传 -----
    UPLOAD_DIR: str = "static/uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_UPLOAD_EXTS: str = "jpg,jpeg,png,gif,webp"

    # ----- 注册与默认管理员 -----
    # 是否开放注册（优先级低于站点设置 allow_register："0"/"false" = 关闭注册）
    ALLOW_REGISTER: bool = True
    # 首次启动是否自动创建默认管理员（仅当库中不存在任何 role=0 用户时）
    AUTO_CREATE_ADMIN: bool = True
    # 默认管理员账号（部署后务必通过环境变量修改 ADMIN_PASSWORD！）
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@kimo.dev"
    ADMIN_PASSWORD: str = "admin123"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        """根据配置拼装 Tortoise 数据库连接串。"""
        if self.DB_ENGINE == "sqlite":
            return "sqlite://db.sqlite3"
        return (
            f"mysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
