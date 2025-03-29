from fastapi import FastAPI

from sqlalchemy import create_engine, text
from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings


# Settings
class Setting(BaseSettings):
    host: str = Field(validation_alias="DB_HOST")
    port: int = Field(validation_alias="DB_PORT")
    username: str = Field(validation_alias="DB_USER")
    password: SecretStr = Field(validation_alias="DB_PASSWORD")
    db: str = Field(validation_alias="DB_NAME")

    @computed_field
    @property
    def uri(self) -> SecretStr:
        return "postgresql://{username}:{password}@{host}:{port}/{db}".format(
            username = self.username,
            password = self.password.get_secret_value(),
            host = self.host,
            port = str(self.port),
            db = self.db
        )


# Main
app = FastAPI()
S = Setting()


@app.get("/")
def main():
    return {
        "status": "OK",
        "message": "Service healthy"
    }

@app.get("/data")
def data():
    engine = create_engine(S.uri)
    with engine.connect() as conn:
        results_conn = conn.execute(text("SELECT * FROM users ORDER BY 1"))
    results = [r for r in results_conn.mappings().all()]
    return results
