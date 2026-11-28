"""
Tu código va aquí. Empieza solo con el Nivel 1.
Cuando pases el nivel, agrega los métodos del siguiente directamente en esta clase
(así funciona en CodeSignal: un solo archivo que va creciendo).

Correr tests:
    python test_cloud_storage.txt cloud_storage_inicio.txt --nivel 1
"""

from __future__ import annotations


class CloudStorage:
    def __init__(self) -> None:
        pass

    # ---------------- Nivel 1 ----------------
    def add_file(self, name: str, size: int) -> bool:
        raise NotImplementedError

    def get_file_size(self, name: str) -> int | None:
        raise NotImplementedError

    def delete_file(self, name: str) -> int | None:
        raise NotImplementedError