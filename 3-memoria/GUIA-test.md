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

---

## Nivel 2 — Scans

### Enunciado

- `scan(timestamp, key) -> list[str]`
  Todos los campos del registro en formato `"field(value)"`, ordenados por `field` ascendente. `[]` si el registro no existe.
- `scan_by_prefix(timestamp, key, prefix) -> list[str]`
  Igual, pero solo los campos cuyo nombre empieza con `prefix`.

---

## Nivel 3 — TTL (tiempo de vida)

### Enunciado

- `set_with_ttl(timestamp, key, field, value, ttl) -> None`
  Como `set`, pero el campo solo existe durante `[timestamp, timestamp + ttl)`. En `timestamp + ttl` ya expiró.
- Todas las operaciones anteriores deben tratar un campo expirado **como si no existiera**: `get` → `None`, `delete` → `False`, `compare_and_set` → `False`, y no aparece en los scans.
- `set` (sin TTL) sobre un campo crea un valor que **no expira**, aunque antes tuviera TTL.
- `compare_and_set` **conserva** la expiración que tuviera el campo.

---

## Nivel 4 — Backup y restore

### Enunciado

- `backup(timestamp) -> int`
  Guarda un snapshot de toda la base en ese momento (solo los campos vivos). Devuelve el número de **registros** (llaves) que tienen al menos un campo vivo. Se conservan **todos** los backups, no solo el último.
- `restore(timestamp, timestamp_to_restore) -> bool`
  Reemplaza toda la base por el backup **más reciente con tiempo ≤ `timestamp_to_restore`**. `False` si no existe ninguno (y no cambia nada).
  - **Recálculo del TTL:** si un campo tenía `R` milisegundos de vida restante al hacer el backup, después del restore vive hasta `timestamp + R`. Los campos sin TTL siguen sin expirar.
  - Los cambios posteriores al backup no deben afectar al snapshot guardado.

---

## Bitácora

```
### Sesión N — fecha
Tiempo: L1 __ / L2 __ / L3 __ / L4 __
Tests: L1 _/7  L2 _/6  L3 _/8  L4 _/9
Hints abiertos:
¿Qué previ bien desde el L1? ¿Qué tuve que refactorizar?
Bug que más tiempo me costó:
```
