"""
Tu código va aquí. Empieza solo con el Nivel 1.
Cuando pases el nivel, agrega los métodos del siguiente directamente en esta clase.

Correr tests:
    python test_editor.txt editor_inicio.txt --nivel 1
"""

from __future__ import annotations
from dataclasses import dataclass, field


State = tuple[str, int, "tuple[int, int] | None"]


@dataclass
class Document:
    text: str = ""
    cursor: int = 0
    selection: tuple[int, int] | None = None
    undo_stack: list[State] = field(default_factory=list)
    redo_stack: list[State] = field(default_factory=list)

    def target_range(self) -> tuple[int, int]:
        return self.selection if self.selection else (self.cursor, self.cursor)

    def norm(self, pos: int) -> int:
        return max(0, min(pos, len(self.text)))

    def snapshot(self) -> State:
        return (self.text, self.cursor, self.selection)

    def restore(self, state: State) -> None:
        self.text, self.cursor, self.selection = state


DEFAULT = "default"


class TextEditor:
    def __init__(self) -> None:
        self._docs = {DEFAULT: Document()}
        self._active = DEFAULT
        self._clipboard = ""

    @property
    def _doc(self):
        return self._docs[self._active]

    def _replace(self, start: int, end: int, new: str) -> None:
        d = self._doc
        snapshot = d.snapshot()
        text = d.text[:start] + new + d.text[end:]
        changed = d.text != text
        d.text = text
        d.cursor = start + len(new) 
        d.selection = None
        if changed:
            d.undo_stack.append(snapshot)
            d.redo_stack.clear()
        
    # ---------------- Nivel 1 ----------------
    def insert(self, text: str) -> str:
        start, end = self._doc.target_range()
        self._replace(start, end, text)
        return self._doc.text

    def move_cursor(self, position: int) -> str:
        d = self._doc
        d.cursor = d.norm(position)
        d.selection = None
        return self._doc.text

    def backspace(self) -> str:
        d = self._doc
        if d.selection:
            self._replace(*d.selection, "")
        elif d.cursor > 0:
            self._replace(d.cursor - 1, d.cursor, "")
        return d.text

    def get_text(self) -> str:
        return self._doc.text

    # ---------------- Nivel 2 ----------------
    def select(self, start, end) -> str:
        d = self._doc
        if start > end:
            start, end = end, start
        if start == end:
            self.move_cursor(start)
        d.selection = start, end
        d.cursor = end
        return d.text

    def copy(self) -> str:
        d = self._doc
        if d.selection:
            start, end = d.selection
            self._clipboard = d.text[start:end]
        return d.text

    def paste(self) -> str:
        d = self._doc
        if self._clipboard:
            self.insert(self._clipboard)
        return d.text

    # ---------------- Nivel 3 ----------------
    def undo(self) -> str:
        d = self._doc
        if d.undo_stack:
            d.redo_stack.append(d.snapshot())
            d.restore(d.undo_stack.pop())
        return d.text


    def redo(self) -> str:
        d = self._doc
        if d.redo_stack:
            d.undo_stack.append(d.snapshot())
            d.restore(d.redo_stack.pop())
        return d.text

    # ---------------- Nivel 4 ----------------
    def create_document(self, name) -> bool:
        if name in self._docs:
            return False
        self._docs[name] = Document()
        return True

    def switch_document(self, name) -> bool:
        if name not in self._docs:
            return False
        self._active = name
        return True

    def delete_document(self, name) -> bool:
        if name not in self._docs or name == self._active:
            return False
        del self._docs[name]
        return True
