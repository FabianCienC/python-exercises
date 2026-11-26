"""
Tu código va aquí. Empieza solo con el Nivel 1.
Cuando pases el nivel, agrega los métodos del siguiente directamente en esta clase.

Correr tests:
    python test_editor.txt editor_inicio.txt --nivel 1
"""

from __future__ import annotations


class TextEditor:
    def __init__(self) -> None:
        pass

    # ---------------- Nivel 1 ----------------
    def insert(self, text: str) -> str:
        raise NotImplementedError

    def move_cursor(self, position: int) -> str:
        raise NotImplementedError

    def backspace(self) -> str:
        raise NotImplementedError

    def get_text(self) -> str:
        raise NotImplementedError
