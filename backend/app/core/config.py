from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, extra="ignore")

    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_name: str = "sigem"
    db_user: str = "sigem"
    mysql_password: SecretStr

    def database_url(self, database: str | None = None) -> URL:
        # URL.create escapa la contraseña: puede tener caracteres especiales
        return URL.create(
            "mysql+pymysql",
            username=self.db_user,
            password=self.mysql_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            database=database or self.db_name,
            query={"charset": "utf8mb4"},
        )


settings = Settings()
