# Práctica 2 — Sistema bancario

---

## Reglas generales del problema

- Todos los métodos reciben `timestamp` (milisegundos). Los timestamps de llamadas sucesivas son **estrictamente crecientes**.
- Montos: enteros positivos. Los saldos nunca pueden quedar negativos.
- Cuando se devuelve `None` o `False` por un error, **no se modifica nada**.

---

## Nivel 2 — Top de cuentas que más gastan

### Enunciado

- `top_spenders(timestamp, n) -> list[str]`
  Devuelve las `n` cuentas con mayor **dinero saliente total**, en formato `"account_id(total)"`.
  - Dinero saliente = transferencias enviadas con éxito (en L3 también se sumarán los pagos). Los depósitos **no** cuentan.
  - Orden: total descendente; si empatan, `account_id` ascendente.
  - Incluye cuentas con total 0. Si hay menos de `n` cuentas, devuelve todas.

---
