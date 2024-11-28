from . import database
import uuid
import secrets
from typing import Optional


class CRUDDocument:
    @staticmethod
    def create(content: str) -> dict:
        embed_id = str(uuid.uuid4())
        auth_key = secrets.token_urlsafe(32)

        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO documents (uuid, content, auth_key) VALUES (?, ?, ?)",
                (embed_id, content, auth_key),
            )
            conn.commit()

        return {"uuid": embed_id, "auth_key": auth_key}

    @staticmethod
    def get(embed_id: str) -> Optional[dict]:
        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM documents WHERE uuid = ?", (embed_id,)
            )
            result = cursor.fetchone()

            if result:
                return dict(result)
            return None

    @staticmethod
    def update(embed_id: str, content: str) -> bool:
        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE documents
                   SET content = ?, last_accessed = CURRENT_TIMESTAMP 
                   WHERE uuid = ?""",
                (content, embed_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(embed_id: str) -> bool:
        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents WHERE uuid = ?", (embed_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted

    @staticmethod
    def cleanup_old_documents(days: int) -> int:
        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """DELETE FROM documents
                   WHERE last_accessed < datetime('now', '-? days')""",
                (days,),
            )
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
