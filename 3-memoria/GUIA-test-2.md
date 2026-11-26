# Práctica 3 — Base de datos en memoria con TTL


## Reglas generales del problema

- La base guarda **registros**: cada registro tiene una `key` y varios `field`, cada uno con un `value` (strings).
- Todos los métodos reciben `timestamp`; los timestamps de llamadas sucesivas son **estrictamente crecientes**.
- Cuando se devuelve `False` o `None` por un error, **no se modifica nada**.

---

## Nivel 2 — Scans

### Enunciado

- `scan(timestamp, key) -> list[str]`
  Todos los campos del registro en formato `"field(value)"`, ordenados por `field` ascendente. `[]` si el registro no existe.
- `scan_by_prefix(timestamp, key, prefix) -> list[str]`
  Igual, pero solo los campos cuyo nombre empieza con `prefix`.

