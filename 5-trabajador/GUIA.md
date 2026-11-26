# Práctica 5 — Gestión de trabajadores

## Objetivo

Practicar un tipo de tiempo distinto al TTL y al cashback: **intervalos**. Entradas y salidas forman sesiones, y hay que calcular cuánto de una sesión cae dentro de un periodo, con tarifas que cambian en el futuro y periodos de doble pago que se traslapan.

**Modo:** sin ayuda. Abre un hint solo si llevas **más de 10 minutos atorado** y anota cuál.

---

## Reglas de práctica

1. Sin IA ni autocompletado inteligente; cronómetro siempre corriendo.
2. Lee **solo el nivel en el que estás**.
3. Un solo archivo que crece.
4. Puedes parar al terminar cualquier nivel.

## Archivos

| Archivo | Para qué |
|---|---|
| `GUIA.md` | Enunciados, subtareas, hints y bitácora |
| `workers_inicio.txt` | Tu código (Python) |
| `test_workers.txt` | Tests por nivel |
| `soluciones/` | Solución y explicación: **no abrir antes de tiempo** |

```bash
python test_workers.txt workers_inicio.txt --nivel 1
python test_workers.txt workers_inicio.txt --nivel 3 -v
```

## Medición

| Nivel | Objetivo | Tu tiempo | Tests | Hints |
|---|---|---|---|---|
| L1 | 10 min | | /7 | |
| L2 | 15 min | | /6 | |
| L3 | 35 min | | /9 | |
| L4 | 25 min | | /8 | |

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

### Subtareas

- [ ] Modela al trabajador y su estado dentro/fuera.
- [ ] Decide qué guardas de cada visita a la oficina: ¿solo un total o algo más?
- [ ] `add_worker`, `register` y `get`.

### Checklist

- Sesión abierta no cuenta · varias sesiones se suman · trabajador recién creado → 0.

<details>
<summary>Hint 1</summary>

Un total acumulado responde `get`, pero imagina preguntas como "¿cuánto trabajó entre el martes y el jueves?" o "¿cuánto se le debe pagar?". ¿Te alcanzaría con un número?

</details>

<details>
<summary>Hint 2</summary>

Guarda cada sesión cerrada como un objeto `Session(start, end, ...)` en una lista del trabajador, y deja espacio para más datos de la sesión. Para dentro/fuera basta `entered_at: int | None`. Mantener además `total_time` como contador es válido y rápido.

</details>

---

## Nivel 2 — Ranking por puesto

### Enunciado

- `top_n_workers(n, position) -> list[str]`
  Los `n` trabajadores con ese puesto que más tiempo han pasado en la oficina, en formato `"worker_id(tiempo)"`.
  - Orden: tiempo descendente; en empate, `worker_id` ascendente.
  - Solo sesiones cerradas. Incluye trabajadores con 0.
  - `[]` si nadie tiene ese puesto.

### Subtareas

- [ ] Filtra por puesto, ordena con la clave de siempre y formatea.

### Checklist

- Empates en 0 · el puesto filtra · `n` mayor que el número de candidatos.

<details>
<summary>Hint 1</summary>

Es el mismo `sorted` con tupla de las prácticas anteriores. Lo único nuevo es filtrar antes.

</details>

<details>
<summary>Hint 2</summary>

`sorted([w for w in workers if w.position == position], key=lambda w: (-tiempo, w.worker_id))[:n]`.

</details>

---

## Nivel 3 — Ascensos y salario

### Enunciado

- `promote(worker_id, new_position, new_compensation, start_timestamp) -> str`
  Programa un ascenso. Entra en vigor la **primera vez que el trabajador entra a la oficina con `timestamp >= start_timestamp`**. Si ya está dentro cuando se cumple la fecha, la sesión en curso sigue con el puesto y la tarifa anteriores.
  Devuelve `"success"`, o `"invalid_request"` si el trabajador no existe o si ya tiene un ascenso **pendiente** (que aún no entra en vigor).
- **Cambio a `top_n_workers`:** a partir de ahora cuenta solo el tiempo en el **puesto actual**. Al entrar en vigor un ascenso, ese contador empieza de cero. `get` sigue devolviendo el tiempo total de todas las sesiones.
- `calc_salary(worker_id, start_timestamp, end_timestamp) -> int | None`
  Salario ganado dentro del periodo `[start, end)`: por cada sesión cerrada, la parte que cae dentro del periodo × la compensación que el trabajador tenía **durante esa sesión**. `None` si no existe.

### Subtareas

- [ ] Guarda el ascenso pendiente y aplícalo en el momento correcto.
- [ ] Separa el "tiempo total" del "tiempo en el puesto actual".
- [ ] Asegúrate de que cada sesión recuerde con qué tarifa se trabajó.
- [ ] `calc_salary` con intersección de intervalos.

### Checklist

- Entrar antes de `start_timestamp` no aplica el ascenso.
- Una sesión que empezó antes del ascenso se paga con la tarifa vieja.
- Periodo que corta una sesión a la mitad → solo cuenta la parte de adentro.
- Después de que entra en vigor, se puede programar otro ascenso.

<details>
<summary>Hint 1</summary>

Si cada sesión guarda su tarifa al **cerrarse**, el historial de pagos nunca se mezcla con la tarifa actual. Y la intersección de dos intervalos `[a1, b1)` y `[a2, b2)` es una fórmula de una línea con `min` y `max`.

</details>

<details>
<summary>Hint 2</summary>

- `Session(start, end, compensation)`, con la compensación vigente al cerrar.
- Ascenso: `pending: Promotion | None`; en `register`, al **entrar**, si `pending and pending.start <= timestamp`, aplica y pon `position_time = 0`.
- Intersección: `max(0, min(b1, b2) - max(a1, a2))`.

</details>

---

## Nivel 4 — Periodos de doble pago

### Enunciado

- `set_double_paid(start_timestamp, end_timestamp) -> None`
  Declara que el tiempo trabajado dentro de `[start, end)` se paga **al doble**.
- `calc_salary` debe tenerlo en cuenta:
  - aplica a todas las sesiones, incluso si el periodo doble se declaró **después** de que se trabajó (es retroactivo);
  - si varios periodos dobles se traslapan, ese tiempo se paga al doble **una sola vez** (no al triple).

### Subtareas

- [ ] Guarda los periodos.
- [ ] Calcula, para cada pedazo de sesión dentro del periodo consultado, cuánto cae en tiempo doble.
- [ ] Evita contar dos veces el tiempo donde los periodos se traslapan.

### Checklist

- Periodos traslapados: `[0, 8)` y `[4, 10)` cubren 10 unidades, no 14.
- Periodos que se tocan (`[0, 5)` y `[5, 10)`) no se traslapan.
- Doble pago fuera del periodo consultado no cuenta.

<details>
<summary>Hint 1</summary>

Pagar el doble es pagar la parte normal más una vez extra la parte en tiempo doble. El problema de los traslapes se resuelve **antes** de intersectar: convierte los periodos en un conjunto sin traslapes.

</details>

<details>
<summary>Hint 2</summary>

- "Merge intervals": ordena los periodos por inicio; si uno empieza antes de que termine el último fusionado, extiende ese; si no, agrega uno nuevo.
- Para cada sesión recortada `[a, b)`: `extra = sum(overlap(a, b, ds, de) for ds, de in fusionados)` y `pago = (b - a + extra) * tarifa`.

</details>

---

## Bitácora

```
### Sesión N — fecha
Tiempo: L1 __ / L2 __ / L3 __ / L4 __
Tests: L1 _/7  L2 _/6  L3 _/9  L4 _/8
Hints abiertos:
¿Qué previ bien desde el L1? ¿Qué tuve que refactorizar?
Bug que más tiempo me costó:
```
