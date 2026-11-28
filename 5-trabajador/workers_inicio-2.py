"""
Tu código va aquí. Empieza solo con el Nivel 1.
Cuando pases el nivel, agrega los métodos del siguiente directamente en esta clase.

Correr tests:
    python test_workers.txt workers_inicio.txt --nivel 1
"""

from __future__ import annotations


class WorkerSystem:
    def __init__(self) -> None:
        pass

    # ---------------- Nivel 1 ----------------
    def add_worker(self, worker_id: str, position: str, compensation: int) -> bool:
        raise NotImplementedError

    def register(self, worker_id: str, timestamp: int) -> str:
        raise NotImplementedError

    def get(self, worker_id: str) -> int | None:
        raise NotImplementedError