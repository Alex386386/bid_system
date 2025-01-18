from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    redis_connect_url: str = "redis://line_redis"
    minimum_event_duration: int = 5000
    # значение по умолчанию в случае отсутствия в .env
    line_provider_token: str = (
        "f3fb8928bad49887d2089f5ad04c2cb634bb1980db77fc8c3b111edad34f4eb7"
    )
    redis_hash_name: str = "redis_hash_name"
    max_id_key: str = "max_id_key"

    rabbit_host: str = "localhost"
    rabbit_port: int = 5672
    rabbit_queue: str = "event_status_updates"


settings = Settings()
