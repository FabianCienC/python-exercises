"""
Tu código va aquí. Empieza solo con el Nivel 1.
Cuando pases el nivel, agrega los métodos del siguiente directamente en esta clase.

Correr tests:
    python test_banco.txt banco_inicio.txt --nivel 1
"""

from __future__ import annotations


class Bank:
    def __init__(self) -> None:
        pass

    # ---------------- Nivel 1 ----------------
    def create_account(self, timestamp: int, account_id: str) -> bool:
        raise NotImplementedError

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        raise NotImplementedError

    def transfer(self, timestamp: int, source_id: str, target_id: str, amount: int) -> int | None:
        raise NotImplementedError
