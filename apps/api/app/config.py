from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://waterpolo:waterpolo@db:5432/waterpolo"
    csv_default_path: str = "/mnt/data/match_data_correct.csv"
    admin_jwt_secret: str = "change-me"
    admin_username: str = "admin"
    admin_password: str = "admin"


settings = Settings()
