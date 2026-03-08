from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


class DatabaseBootstrapError(Exception):
    pass


class UnsupportedDatabaseBootstrapError(DatabaseBootstrapError):
    pass


def build_maintenance_database_url(database_url: str) -> str:
    url = make_url(database_url)
    if not url.drivername.startswith("postgresql"):
        raise UnsupportedDatabaseBootstrapError()
    return url.set(database="postgres").render_as_string(hide_password=False)


def _get_target_database_name(database_url: str) -> str:
    url = make_url(database_url)
    if not url.database:
        raise DatabaseBootstrapError()
    return url.database


def ensure_database_exists(database_url: str) -> None:
    maintenance_url = build_maintenance_database_url(database_url)
    target_database = _get_target_database_name(database_url)
    engine = create_engine(maintenance_url, future=True, isolation_level="AUTOCOMMIT")

    try:
        with engine.begin() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
                {"database_name": target_database},
            ).scalar()
            if exists:
                return

            quoted_database_name = engine.dialect.identifier_preparer.quote(target_database)
            connection.execute(text(f"CREATE DATABASE {quoted_database_name}"))
    except UnsupportedDatabaseBootstrapError:
        raise
    except Exception as exc:
        raise DatabaseBootstrapError() from exc
    finally:
        engine.dispose()
