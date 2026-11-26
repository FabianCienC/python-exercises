# Práctica 4 — Editor de texto

---

## Reglas generales del problema

- El editor tiene un **texto** y un **cursor**: una posición entre caracteres, de `0` (antes del primero) a `len(texto)` (después del último). Al inicio, el texto está vacío y el cursor en `0`.
- Todos los métodos devuelven el **texto completo** después de la operación.

---

## Nivel 1 — Escribir y borrar

### Enunciado

- `insert(text) -> str`
  Inserta `text` en la posición del cursor. El cursor queda **justo después** de lo insertado.
- `move_cursor(position) -> str`
  Mueve el cursor a `position`. Si está fuera de rango, se ajusta al límite más cercano (`< 0` → `0`, `> len` → `len`).
- `backspace() -> str`
  Borra el carácter **antes** del cursor y el cursor retrocede uno. Si el cursor está en `0`, no hace nada.
- `get_text() -> str`
  Devuelve el texto.

---
