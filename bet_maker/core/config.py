from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    db_engine: str
    db_name: str
    postgres_user: str
    postgres_password: str
    db_host: str
    db_port: int

    secret_key: str
    algorithm: str
    token_expired_minutes: int = 3600

    event_url: str

    rabbit_host: str = "localhost"
    rabbit_port: int = 5672
    rabbit_queue: str = "event_status_updates"
    line_provider_token: str = (
        "f3fb8928bad49887d2089f5ad04c2cb634bb1980db77fc8c3b111edad34f4eb7"
    )

    cache_max_size: int = 100
    cache_ttl: int = 60

    first_user_username: str = "string"
    first_user_email: str = "example@example.com"
    first_user_password: str = "string"
    first_user_name: str = "string"


settings = Settings()
