# Práctica 2 — Sistema bancario

---

## Reglas generales del problema

- Todos los métodos reciben `timestamp` (milisegundos). Los timestamps de llamadas sucesivas son **estrictamente crecientes**.
- Montos: enteros positivos. Los saldos nunca pueden quedar negativos.
- Cuando se devuelve `None` o `False` por un error, **no se modifica nada**.

---

## Nivel 1 — Cuentas, depósitos y transferencias

### Enunciado

- `create_account(timestamp, account_id) -> bool`
  Crea una cuenta con saldo 0. `False` si ya existe.
- `deposit(timestamp, account_id, amount) -> int | None`
  Suma `amount` al saldo y devuelve el saldo nuevo. `None` si la cuenta no existe.
- `transfer(timestamp, source_id, target_id, amount) -> int | None`
  Mueve `amount` de `source` a `target` y devuelve el saldo nuevo de `source`.
  `None` si alguna cuenta no existe, si son la misma cuenta o si `source` no tiene saldo suficiente.

---

## Nivel 2 — Top de cuentas que más gastan

### Enunciado

- `top_spenders(timestamp, n) -> list[str]`
  Devuelve las `n` cuentas con mayor **dinero saliente total**, en formato `"account_id(total)"`.
  - Dinero saliente = transferencias enviadas con éxito (en L3 también se sumarán los pagos). Los depósitos **no** cuentan.
  - Orden: total descendente; si empatan, `account_id` ascendente.
  - Incluye cuentas con total 0. Si hay menos de `n` cuentas, devuelve todas.

---

## Nivel 3 — Pagos con cashback programado

### Enunciado

- `pay(timestamp, account_id, amount) -> str | None`
  Retira `amount` de la cuenta (cuenta como dinero saliente para `top_spenders`) y devuelve un id de pago con el formato `"payment1"`, `"payment2"`, … Los ids son **globales** (no por cuenta) y solo los pagos exitosos consumen número.
  `None` si la cuenta no existe o no tiene saldo suficiente.
- **Cashback:** cada pago genera un cashback del **2 % redondeado hacia abajo**, que se acredita a la cuenta exactamente **24 horas después** (`timestamp + 86_400_000`).
  - El cashback **no** reduce el dinero saliente.
  - Los cashbacks que vencen en un timestamp `T` se procesan **antes** de cualquier operación en `T` (y antes de cualquier operación posterior). Si vencen varios a la vez, se procesan en el orden en que se crearon los pagos.
- `get_payment_status(timestamp, account_id, payment_id) -> str | None`
  `"IN_PROGRESS"` si el cashback no ha llegado; `"CASHBACK_RECEIVED"` si ya llegó.
  `None` si la cuenta no existe, si el pago no existe o si el pago no pertenece a esa cuenta.

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
