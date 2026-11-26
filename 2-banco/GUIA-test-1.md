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

## Bitácora

```
### Sesión N — fecha
Tiempo: L1 __ / L2 __ / L3 __ / L4 __
Tests: L1 _/7  L2 _/6  L3 _/8  L4 _/9
Hints abiertos:
¿Qué previ bien desde el L1? ¿Qué tuve que refactorizar?
Bug que más tiempo me costó:
```
