# Práctica 4 — Editor de texto

---

## Reglas generales del problema

- El editor tiene un **texto** y un **cursor**: una posición entre caracteres, de `0` (antes del primero) a `len(texto)` (después del último). Al inicio, el texto está vacío y el cursor en `0`.
- Todos los métodos devuelven el **texto completo** después de la operación.

---

## Nivel 4 — Varios documentos

### Enunciado

- Al inicio existe un documento llamado `"default"`, que es el activo. Todas las operaciones anteriores actúan sobre el **documento activo**.
- `create_document(name) -> bool`
  Crea un documento vacío (no lo activa). `False` si ya existe.
- `switch_document(name) -> bool`
  Cambia el documento activo. `False` si no existe (y el activo no cambia).
- `delete_document(name) -> bool`
  Borra el documento. `False` si no existe o si es el activo.
- Cada documento tiene su **propio** texto, cursor, selección e historial de undo/redo.
- El **portapapeles es compartido** entre todos los documentos.