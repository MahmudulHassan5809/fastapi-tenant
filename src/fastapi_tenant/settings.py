from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    TENANT_HEADER: str = "X-Tenant-ID"
    DEFAULT_SCHEMA: str = "public"
    ENABLE_SUBDOMAIN_RESOLVER: bool = True
    PATH_PREFIX: str = "/t"
    ALEMBIC_INI: str = "alembic.ini"
    MIGRATION_TENANT_TABLE: str = "public.tenants"
    MIGRATION_LOCK_ID: int = 4242001

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
