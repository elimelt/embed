import sqlite3
from contextlib import contextmanager
from ..config import settings


@contextmanager
def get_db():
    conn = sqlite3.connect(settings.DATABASE_URL)
    try:
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                uuid TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                auth_key TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        conn.commit()
