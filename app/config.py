from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_bot_token: str
    telegram_allowed_users: str = ""
    anthropic_api_key: str
    openai_api_key: str = ""
    database_url: str = "sqlite+aiosqlite:///./data/linkedin_automation.db"
    linkedin_image_width: int = 1200
    linkedin_image_height: int = 627

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def allowed_user_ids(self) -> list[int]:
        if not self.telegram_allowed_users:
            return []
        return [int(uid.strip()) for uid in self.telegram_allowed_users.split(",")]


settings = Settings()
