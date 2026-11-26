# Práctica 5 — Gestión de trabajadores

---

## Reglas generales del problema

- Una empresa registra cuándo entran y salen sus trabajadores de la oficina.
- Los timestamps de `register` son **estrictamente crecientes** entre llamadas.
- Todos los intervalos son **semiabiertos**: `[inicio, fin)`. Una sesión de 10 a 25 dura 15.

---

## Nivel 1 — Registro de entradas y salidas

### Enunciado

- `add_worker(worker_id, position, compensation) -> bool`
  Agrega un trabajador con su puesto y su compensación (pago por unidad de tiempo). `False` si ya existe.
- `register(worker_id, timestamp) -> str`
  Si el trabajador está fuera, **entra** en `timestamp`; si está dentro, **sale**. Devuelve `"registered"`, o `"invalid_request"` si el trabajador no existe.
- `get(worker_id) -> int | None`
  Tiempo total que el trabajador ha pasado en la oficina, sumando solo las sesiones **cerradas** (la sesión en curso no cuenta). `None` si no existe.
