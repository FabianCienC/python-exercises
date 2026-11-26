# Práctica 3 — Base de datos en memoria con TTL


## Reglas generales del problema

- La base guarda **registros**: cada registro tiene una `key` y varios `field`, cada uno con un `value` (strings).
- Todos los métodos reciben `timestamp`; los timestamps de llamadas sucesivas son **estrictamente crecientes**.
- Cuando se devuelve `False` o `None` por un error, **no se modifica nada**.

---

## Nivel 1 — Operaciones básicas

### Enunciado

- `set(timestamp, key, field, value) -> None`
  Guarda `value` en `field` del registro `key` (crea el registro si no existe; sobrescribe si el campo ya existía).
- `get(timestamp, key, field) -> str | None`
  Valor del campo, o `None` si el registro o el campo no existen.
- `delete(timestamp, key, field) -> bool`
  Borra el campo. `True` si existía, `False` si no. Si el registro se queda sin campos, deja de existir.
- `compare_and_set(timestamp, key, field, expected, new_value) -> bool`
  Si el campo existe y su valor actual es `expected`, lo cambia a `new_value` y devuelve `True`. Si no, `False` (y no crea nada).
