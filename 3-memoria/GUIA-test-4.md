# Práctica 3 — Base de datos en memoria con TTL


## Reglas generales del problema

- La base guarda **registros**: cada registro tiene una `key` y varios `field`, cada uno con un `value` (strings).
- Todos los métodos reciben `timestamp`; los timestamps de llamadas sucesivas son **estrictamente crecientes**.
- Cuando se devuelve `False` o `None` por un error, **no se modifica nada**.

---

## Nivel 4 — Backup y restore

### Enunciado

- `backup(timestamp) -> int`
  Guarda un snapshot de toda la base en ese momento (solo los campos vivos). Devuelve el número de **registros** (llaves) que tienen al menos un campo vivo. Se conservan **todos** los backups, no solo el último.
- `restore(timestamp, timestamp_to_restore) -> bool`
  Reemplaza toda la base por el backup **más reciente con tiempo ≤ `timestamp_to_restore`**. `False` si no existe ninguno (y no cambia nada).
  - **Recálculo del TTL:** si un campo tenía `R` milisegundos de vida restante al hacer el backup, después del restore vive hasta `timestamp + R`. Los campos sin TTL siguen sin expirar.
  - Los cambios posteriores al backup no deben afectar al snapshot guardado.

