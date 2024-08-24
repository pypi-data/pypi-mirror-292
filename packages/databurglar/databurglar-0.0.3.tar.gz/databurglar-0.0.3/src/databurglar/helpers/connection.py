from dataclasses import dataclass
from sqlalchemy import create_engine, Engine


@dataclass
class DatabaseConnection:
    user: str
    password: str
    host: str
    port: int
    database: str


def connect_to_pg(conn: DatabaseConnection) -> Engine:
    return create_engine(
        url=f'postgresql://{conn.user}:{conn.password}@{conn.host}:{conn.port}/{conn.database}'
    )
