from __future__ import annotations

from werkzeug.security import check_password_hash

from models.db_sqlite import query_sqlite


class User:

    def __init__(self, id: int, username: str, role: str, nombre: str):
        self.id = id
        self.username = username
        self.role = role
        self.nombre = nombre

    @staticmethod
    def authenticate(username: str, password: str) -> "User | None":
        row = query_sqlite(
            "SELECT id, username, password_hash, role, nombre FROM users WHERE username = ?",
            (username.strip(),),
            one=True,
        )
        if row and check_password_hash(row["password_hash"], password):
            return User(row["id"], row["username"], row["role"], row["nombre"])
        return None
