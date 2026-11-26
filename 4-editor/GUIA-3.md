# Práctica 4 — Editor de texto

---

## Reglas generales del problema

- El editor tiene un **texto** y un **cursor**: una posición entre caracteres, de `0` (antes del primero) a `len(texto)` (después del último). Al inicio, el texto está vacío y el cursor en `0`.
- Todos los métodos devuelven el **texto completo** después de la operación.

---

## Nivel 3 — Undo y redo

### Enunciado

- `undo() -> str`
  Deshace la última operación que **cambió el texto** (`insert`, `backspace` o `paste`), restaurando texto, cursor **y selección** a como estaban justo antes. Si no hay nada que deshacer, no hace nada.
- `redo() -> str`
  Rehace la última operación deshecha, restaurando el estado que había antes de ese `undo`. Si no hay nada que rehacer, no hace nada.
- Cualquier operación nueva que cambie el texto **borra** el historial de redo.
- `move_cursor`, `select` y `copy` **no** se registran: un `undo` después de ellos deshace la última edición real.
- Una operación que no cambia el texto (por ejemplo, `backspace` en la posición 0 o `paste` con el portapapeles vacío) **no** se registra.
