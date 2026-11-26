# Práctica 5 — Gestión de trabajadores

---

## Reglas generales del problema

- Una empresa registra cuándo entran y salen sus trabajadores de la oficina.
- Los timestamps de `register` son **estrictamente crecientes** entre llamadas.
- Todos los intervalos son **semiabiertos**: `[inicio, fin)`. Una sesión de 10 a 25 dura 15.

---

## Nivel 2 — Ranking por puesto

### Enunciado

- `top_n_workers(n, position) -> list[str]`
  Los `n` trabajadores con ese puesto que más tiempo han pasado en la oficina, en formato `"worker_id(tiempo)"`.
  - Orden: tiempo descendente; en empate, `worker_id` ascendente.
  - Solo sesiones cerradas. Incluye trabajadores con 0.
  - `[]` si nadie tiene ese puesto.
