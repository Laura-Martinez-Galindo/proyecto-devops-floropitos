import os

from sqlalchemy.engine import URL


def build_database_uri():
    # Beanstalk expone estas variables cuando la RDS esta asociada al entorno
    if os.environ.get("RDS_HOSTNAME"):
        return URL.create(
            "postgresql+psycopg2",
            username=os.environ["RDS_USERNAME"],
            password=os.environ["RDS_PASSWORD"],
            host=os.environ["RDS_HOSTNAME"],
            port=int(os.environ.get("RDS_PORT", 5432)),
            database=os.environ["RDS_DB_NAME"],
        )
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/blacklist",
    )


class Config:
    SQLALCHEMY_DATABASE_URI = build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-cambiar")
    PROPAGATE_EXCEPTIONS = True
