from pydantic import BaseSettings


class Settings(BaseSettings):
    upload_folder: str
    complete_stack_error: bool

    class Config:
        env_file = "app/.env"


settings = Settings()
