from sqlalchemy import create_engine
from sqlalchemy.engine import URL, make_url


class BaseDatabaseProvider:
    name: str = ""

    def supports(self, url: URL) -> bool:
        raise NotImplementedError

    def create_engine(self, database_url: str):
        return create_engine(database_url, future=True)


class SQLiteDatabaseProvider(BaseDatabaseProvider):
    name = "sqlite"

    def supports(self, url: URL) -> bool:
        return url.drivername.startswith("sqlite")


class PostgreSQLDatabaseProvider(BaseDatabaseProvider):
    name = "postgresql"

    def supports(self, url: URL) -> bool:
        return url.drivername.startswith("postgresql")


DATABASE_PROVIDERS: dict[str, BaseDatabaseProvider] = {
    "sqlite": SQLiteDatabaseProvider(),
    "postgresql": PostgreSQLDatabaseProvider(),
}


def resolve_database_provider(database_url: str) -> BaseDatabaseProvider:
    url = make_url(database_url)
    for provider in DATABASE_PROVIDERS.values():
        if provider.supports(url):
            return provider
    raise ValueError(f"unsupported_database_driver:{url.drivername}")
