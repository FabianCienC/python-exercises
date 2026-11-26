# Práctica 5 — Gestión de trabajadores

---

## Reglas generales del problema

- Una empresa registra cuándo entran y salen sus trabajadores de la oficina.
- Los timestamps de `register` son **estrictamente crecientes** entre llamadas.
- Todos los intervalos son **semiabiertos**: `[inicio, fin)`. Una sesión de 10 a 25 dura 15.

---

## Nivel 4 — Periodos de doble pago

### Enunciado

- `set_double_paid(start_timestamp, end_timestamp) -> None`
  Declara que el tiempo trabajado dentro de `[start, end)` se paga **al doble**.
- `calc_salary` debe tenerlo en cuenta:
  - aplica a todas las sesiones, incluso si el periodo doble se declaró **después** de que se trabajó (es retroactivo);
  - si varios periodos dobles se traslapan, ese tiempo se paga al doble **una sola vez** (no al triple).

---

