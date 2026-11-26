# Práctica 2 — Sistema bancario

---

## Reglas generales del problema

- Todos los métodos reciben `timestamp` (milisegundos). Los timestamps de llamadas sucesivas son **estrictamente crecientes**.
- Montos: enteros positivos. Los saldos nunca pueden quedar negativos.
- Cuando se devuelve `None` o `False` por un error, **no se modifica nada**.

---

## Nivel 4 — Fusión de cuentas y saldo histórico

### Enunciado

- `merge_accounts(timestamp, target_id, source_id) -> bool`
  Fusiona `source` dentro de `target`:
  - el saldo y el dinero saliente de `source` se suman a `target`;
  - los pagos de `source` pasan a ser de `target`: sus cashbacks pendientes se acreditarán a `target`, y su estado se consulta con `target_id`;
  - `source` deja de existir (su id puede volver a crearse como cuenta nueva).

  `False` si son la misma cuenta o si alguna no existe.
- `get_balance(timestamp, account_id, time_at) -> int | None`
  Devuelve el saldo que tenía la cuenta en el tiempo `time_at` (`time_at <= timestamp`), **incluyendo** todas las operaciones con timestamp `time_at`.
  - `None` si la cuenta no existe ahora o si no existía en `time_at` (todavía no se había creado).
  - Los cashbacks cuentan en su tiempo de vencimiento.
  - Para la cuenta `target` de un merge, antes del merge solo cuenta su saldo propio; el saldo de `source` se suma a partir del timestamp del merge.

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
