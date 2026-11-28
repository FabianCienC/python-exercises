"""
Tu código va aquí. Empieza solo con el Nivel 1.
Cuando pases el nivel, agrega los métodos del siguiente directamente en esta clase.

Correr tests:
    python test_db.txt db_inicio.txt --nivel 1
"""

from __future__ import annotations


class InMemoryDB:
    def __init__(self) -> None:
        pass

    # ---------------- Nivel 1 ----------------
    def set(self, timestamp: int, key: str, field: str, value: str) -> None:
        raise NotImplementedError

    def get(self, timestamp: int, key: str, field: str) -> str | None:
        raise NotImplementedError

    def delete(self, timestamp: int, key: str, field: str) -> bool:
        raise NotImplementedError

    def compare_and_set(self, timestamp: int, key: str, field: str,
                        expected: str, new_value: str) -> bool:
        raise NotImplementedError