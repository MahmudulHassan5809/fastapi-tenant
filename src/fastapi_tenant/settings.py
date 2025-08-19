from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    DEBUG: bool = True
    TENANT_HEADER: str = "X-Tenant-ID"
    DEFAULT_SCHEMA: str = "public"
    ENABLE_SUBDOMAIN_RESOLVER: bool = True
    PATH_PREFIX: str = "/t"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
