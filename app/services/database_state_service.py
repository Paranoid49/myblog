from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.core.config import settings


def database_exists() -> bool:
    url = make_url(settings.database_url)
    if not url.drivername.startswith("postgresql"):
        return True

    engine = create_engine(str(url.set(database="postgres")), future=True)
    try:
        with engine.connect() as connection:
            return bool(
                connection.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
                    {"database_name": url.database},
                ).scalar()
            )
    except Exception:
        return False
    finally:
        engine.dispose()
