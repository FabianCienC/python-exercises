# Práctica 4 — Editor de texto

---

## Reglas generales del problema

- El editor tiene un **texto** y un **cursor**: una posición entre caracteres, de `0` (antes del primero) a `len(texto)` (después del último). Al inicio, el texto está vacío y el cursor en `0`.
- Todos los métodos devuelven el **texto completo** después de la operación.

---

## Nivel 2 — Selección, copiar y pegar

### Enunciado

- `select(start, end) -> str`
  Selecciona el rango `[start, end)`. Ambos valores se ajustan a `[0, len]`; si `start > end`, se intercambian. Si quedan iguales, equivale a `move_cursor(start)`. Después de seleccionar, el cursor queda en `end`.
- Con una selección activa:
  - `insert(text)` **reemplaza** la selección por `text`;
  - `backspace()` **borra** la selección y el cursor queda donde empezaba.

  En ambos casos la selección desaparece.
- `move_cursor` quita la selección.
- `copy() -> str`
  Si hay selección, copia su contenido al portapapeles (sin modificar el texto ni la selección). Si no hay selección, no hace nada.
- `paste() -> str`
  Se comporta exactamente como `insert(portapapeles)`, incluido reemplazar la selección. Al inicio, el portapapeles está vacío.

