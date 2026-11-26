# Práctica 5 — Gestión de trabajadores

---

## Reglas generales del problema

- Una empresa registra cuándo entran y salen sus trabajadores de la oficina.
- Los timestamps de `register` son **estrictamente crecientes** entre llamadas.
- Todos los intervalos son **semiabiertos**: `[inicio, fin)`. Una sesión de 10 a 25 dura 15.

---

## Nivel 3 — Ascensos y salario

### Enunciado

- `promote(worker_id, new_position, new_compensation, start_timestamp) -> str`
  Programa un ascenso. Entra en vigor la **primera vez que el trabajador entra a la oficina con `timestamp >= start_timestamp`**. Si ya está dentro cuando se cumple la fecha, la sesión en curso sigue con el puesto y la tarifa anteriores.
  Devuelve `"success"`, o `"invalid_request"` si el trabajador no existe o si ya tiene un ascenso **pendiente** (que aún no entra en vigor).
- **Cambio a `top_n_workers`:** a partir de ahora cuenta solo el tiempo en el **puesto actual**. Al entrar en vigor un ascenso, ese contador empieza de cero. `get` sigue devolviendo el tiempo total de todas las sesiones.
- `calc_salary(worker_id, start_timestamp, end_timestamp) -> int | None`
  Salario ganado dentro del periodo `[start, end)`: por cada sesión cerrada, la parte que cae dentro del periodo × la compensación que el trabajador tenía **durante esa sesión**. `None` si no existe.
