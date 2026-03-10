from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Hostel Booking API"
    secret_key: str = "CHANGE_ME"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "sqlite+aiosqlite:///./hostel.db"

    class Config:
        env_file = ".env"


settings = Settings()