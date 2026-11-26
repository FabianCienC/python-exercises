# Práctica 2 — Sistema bancario

---

## Reglas generales del problema

- Todos los métodos reciben `timestamp` (milisegundos). Los timestamps de llamadas sucesivas son **estrictamente crecientes**.
- Montos: enteros positivos. Los saldos nunca pueden quedar negativos.
- Cuando se devuelve `None` o `False` por un error, **no se modifica nada**.

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
