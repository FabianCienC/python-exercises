# Práctica 3 — Base de datos en memoria con TTL


## Reglas generales del problema

- La base guarda **registros**: cada registro tiene una `key` y varios `field`, cada uno con un `value` (strings).
- Todos los métodos reciben `timestamp`; los timestamps de llamadas sucesivas son **estrictamente crecientes**.
- Cuando se devuelve `False` o `None` por un error, **no se modifica nada**.

---

## Nivel 3 — TTL (tiempo de vida)

### Enunciado

- `set_with_ttl(timestamp, key, field, value, ttl) -> None`
  Como `set`, pero el campo solo existe durante `[timestamp, timestamp + ttl)`. En `timestamp + ttl` ya expiró.
- Todas las operaciones anteriores deben tratar un campo expirado **como si no existiera**: `get` → `None`, `delete` → `False`, `compare_and_set` → `False`, y no aparece en los scans.
- `set` (sin TTL) sobre un campo crea un valor que **no expira**, aunque antes tuviera TTL.
- `compare_and_set` **conserva** la expiración que tuviera el campo.

