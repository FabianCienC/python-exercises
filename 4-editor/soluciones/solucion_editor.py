"""
SOLUCIÓN DE REFERENCIA — Editor de texto (L1–L4)

No abras este archivo hasta haber intentado el nivel correspondiente.
Correr tests contra esta solución (desde la carpeta principal):
    python test_editor.txt soluciones/solucion_editor.txt

Ideas clave (detalle en SOLUCION.md):
  1. TODO el estado editable (texto, cursor, selección, historial) vive en un objeto Document
     desde el L1. En el L4 (varios documentos) solo cambia "cuál documento está activo".
  2. Toda modificación de texto pasa por un solo helper: _replace(start, end, nuevo).
     insert, backspace y paste son casos particulares de "reemplazar un rango".
  3. Undo/redo con snapshots inmutables (tupla texto, cursor, selección) en dos pilas.
     El helper registra el snapshot ANTES de modificar; una edición nueva vacía redo.
"""

from __future__ import annotations

from dataclasses import dataclass, field

DEFAULT_DOC = "default"

# (texto, cursor, selección) — tupla de valores inmutables: segura para guardar en pilas
State = tuple[str, int, "tuple[int, int] | None"]


@dataclass
class Document:
    text: str = ""
    cursor: int = 0
    selection: tuple[int, int] | None = None     # rango [start, end) con start < end
    undo_stack: list[State] = field(default_factory=list)
    redo_stack: list[State] = field(default_factory=list)

    def snapshot(self) -> State:
        return (self.text, self.cursor, self.selection)

    def restore(self, state: State) -> None:
        self.text, self.cursor, self.selection = state

    def clamp(self, pos: int) -> int:
        return max(0, min(pos, len(self.text)))

    def target_range(self) -> tuple[int, int]:
        """Rango sobre el que actúa una edición: la selección o el cursor."""
        return self.selection if self.selection else (self.cursor, self.cursor)


class TextEditor:
    def __init__(self) -> None:
        self._docs: dict[str, Document] = {DEFAULT_DOC: Document()}
        self._active = DEFAULT_DOC
        self._clipboard = ""          # compartido entre documentos (L4)

    @property
    def _doc(self) -> Document:
        return self._docs[self._active]

    # ------------------------------------------------------------------
    # Helper central: único lugar que modifica el texto
    # ------------------------------------------------------------------
    def _replace(self, start: int, end: int, new: str) -> None:
        d = self._doc
        before = d.snapshot()
        new_text = d.text[:start] + new + d.text[end:]
        changed = new_text != d.text
        d.text = new_text
        d.cursor = start + len(new)
        d.selection = None
        if changed:                     # L3: solo los cambios reales entran al historial
            d.undo_stack.append(before)
            d.redo_stack.clear()

    # ------------------------------------------------------------------
    # Nivel 1
    # ------------------------------------------------------------------
    def insert(self, text: str) -> str:
        start, end = self._doc.target_range()
        self._replace(start, end, text)
        return self._doc.text

    def move_cursor(self, position: int) -> str:
        d = self._doc
        d.cursor = d.clamp(position)
        d.selection = None
        return d.text

    def backspace(self) -> str:
        d = self._doc
        if d.selection:
            self._replace(*d.selection, "")
        elif d.cursor > 0:
            self._replace(d.cursor - 1, d.cursor, "")
        return d.text

    def get_text(self) -> str:
        return self._doc.text

    # ------------------------------------------------------------------
    # Nivel 2
    # ------------------------------------------------------------------
    def select(self, start: int, end: int) -> str:
        d = self._doc
        start, end = d.clamp(start), d.clamp(end)
        if start > end:
            start, end = end, start
        if start == end:
            return self.move_cursor(start)
        d.selection = (start, end)
        d.cursor = end
        return d.text

    def copy(self) -> str:
        d = self._doc
        if d.selection:
            start, end = d.selection
            self._clipboard = d.text[start:end]
        return d.text

    def paste(self) -> str:
        return self.insert(self._clipboard)

    # ------------------------------------------------------------------
    # Nivel 3
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Nivel 4
    # ------------------------------------------------------------------
    def create_document(self, name: str) -> bool:
        if name in self._docs:
            return False
        self._docs[name] = Document()
        return True

    def switch_document(self, name: str) -> bool:
        if name not in self._docs:
            return False
        self._active = name
        return True

    def delete_document(self, name: str) -> bool:
        if name not in self._docs or name == self._active:
            return False
        del self._docs[name]
        return True
