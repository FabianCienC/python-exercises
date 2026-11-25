# Práctica 2 — Sistema bancario

## Objetivo

Practicar un problema ICA donde **el tiempo importa desde el L1**: todos los métodos reciben `timestamp`. Los patrones clave son **eventos programados** (L3) y **consultas históricas** (L4).

**Modo recomendado:** ahora que ya conoces el formato, trátalo como semi-simulacro. Abre un hint solo si llevas **más de 10 minutos atorado** en algo, y anota cuál abriste.

---

## Reglas de práctica

1. Sin IA ni autocompletado inteligente; cronómetro siempre corriendo.
2. Lee **solo el nivel en el que estás**. No leas los siguientes: en el examen no puedes verlos.
3. Un solo archivo que crece.
4. Puedes parar al terminar cualquier nivel.

## Archivos

| Archivo | Para qué |
|---|---|
| `GUIA.md` | Enunciados, subtareas, hints y bitácora |
| `banco_inicio.txt` | Tu código (Python) |
| `test_banco.txt` | Tests por nivel |
| `soluciones/` | Solución y explicación: **no abrir antes de tiempo** |

```bash
python test_banco.txt banco_inicio.txt --nivel 1
python test_banco.txt banco_inicio.txt --nivel 3 -v
```

## Medición

| Nivel | Objetivo | Tu tiempo | Tests | Hints |
|---|---|---|---|---|
| L1 | 10 min | | /7 | |
| L2 | 15 min | | /6 | |
| L3 | 30 min | | /8 | |
| L4 | 35 min | | /9 | |

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

### Subtareas

- [ ] Modela la cuenta (piensa en qué más podría necesitar saber una cuenta bancaria además de su saldo).
- [ ] `create_account` y `deposit`.
- [ ] `transfer` con todas sus validaciones antes de mover dinero.

### Checklist

- Transferir exactamente todo el saldo (debe quedar 0).
- Transferir a la misma cuenta.
- Un transfer fallido no cambia ningún saldo.

<details>
<summary>Hint 1 (conceptual)</summary>

Todos los métodos reciben `timestamp` aunque hoy no lo uses. Esa es la señal más fuerte del examen: el tiempo va a importar. ¿Qué información sobre la *historia* de una cuenta podría pedirse después, y desde qué único lugar del código cambias un saldo?

</details>

<details>
<summary>Hint 2 (concreto)</summary>

Usa una dataclass `Account` y un helper `_change_balance(account, delta, ts)` por el que pase **todo** cambio de saldo (depósito, salida y entrada de transferencia). Hoy solo suma; mañana puede registrar historial sin tocar los métodos públicos.

</details>

---

## Nivel 2 — Top de cuentas que más gastan

### Enunciado

- `top_spenders(timestamp, n) -> list[str]`
  Devuelve las `n` cuentas con mayor **dinero saliente total**, en formato `"account_id(total)"`.
  - Dinero saliente = transferencias enviadas con éxito (en L3 también se sumarán los pagos). Los depósitos **no** cuentan.
  - Orden: total descendente; si empatan, `account_id` ascendente.
  - Incluye cuentas con total 0. Si hay menos de `n` cuentas, devuelve todas.

### Subtareas

- [ ] Decide dónde y cuándo acumular el dinero saliente (¿calcularlo cada vez o mantenerlo?).
- [ ] Ordena, recorta y formatea.

### Checklist

- Empates en 0 · transfers fallidos no cuentan · `n` mayor que el número de cuentas.

<details>
<summary>Hint 1</summary>

Mantener un contador por cuenta que se actualiza en cada salida exitosa es O(1) por operación, y el ranking es solo un `sorted`.

</details>

<details>
<summary>Hint 2</summary>

Campo `outgoing` en `Account`; en `transfer`, `source.outgoing += amount` después de validar. Clave de orden: `(-a.outgoing, a.account_id)`.

</details>

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

### Subtareas

- [ ] Modela el pago (¿qué necesitas saber de él para acreditarlo después y para reportar su estado?).
- [ ] Implementa `pay` con su id global.
- [ ] Diseña la estructura de cashbacks pendientes: necesitas sacar siempre "el que vence primero".
- [ ] Haz que **todos** los métodos públicos procesen los cashbacks vencidos antes de hacer cualquier otra cosa.
- [ ] `get_payment_status`.

### Checklist

- El cashback llega en `ts + 24h` exacto, no un milisegundo antes.
- Redondeo: pagar 149 da cashback de 2.
- Un cashback que vence en `T` ya está disponible para una transferencia en `T`.

<details>
<summary>Hint 1</summary>

"Siempre el que vence primero" es un **min-heap**. Y no hay ningún reloj corriendo: el sistema solo "despierta" cuando lo llaman, así que cada método debe ponerse al día primero.

</details>

<details>
<summary>Hint 2</summary>

- `heapq.heappush(self._pending, (due, numero_de_pago, payment_id))`; el número desempata por orden de creación.
- Helper `_process_due(ts)`: mientras `self._pending[0][0] <= ts`, saca, acredita (con tu `_change_balance`) y marca el pago como recibido. Llámalo en la primera línea de cada método público.
- Ids: `itertools.count(1)` y `f"payment{next(...)}"`.
- Cashback entero: `amount * 2 // 100`.

</details>

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

### Subtareas

- [ ] `merge_accounts`: valida y luego transfiere saldo, salidas y pagos.
- [ ] Decide cómo guardar el historial de saldos (¿qué estructura te deja responder "el último valor con tiempo ≤ T" rápido?).
- [ ] Asegúrate de que **todo** cambio de saldo quede registrado, incluido el cashback en su tiempo de vencimiento.
- [ ] `get_balance`.

### Checklist

- Consulta antes de la creación → `None`.
- Consulta exactamente en el timestamp de una operación → saldo *después* de esa operación.
- Una cuenta re-creada con un id fusionado empieza de cero y sin historial previo.

<details>
<summary>Hint 1</summary>

Si en el L1 hiciste que todo cambio de saldo pase por un helper, el historial es agregar dos líneas ahí. Como los timestamps llegan en orden creciente, una lista de `(tiempo, saldo)` ya está ordenada, así que puedes buscar con búsqueda binaria.

</details>

<details>
<summary>Hint 2</summary>

- Listas paralelas `history_ts` y `history_bal` por cuenta; registra en `create_account` y en `_change_balance`.
- Si ya hay un registro con el mismo timestamp, sobrescríbelo (el saldo "en `T`" es el final de `T`).
- `i = bisect.bisect_right(history_ts, time_at) - 1` → `None` si `i < 0`.
- Al acreditar un cashback, registra con su `due`, no con el `timestamp` actual.
- En el merge, el pago guarda `account_id`: reasígnalo y el cashback pendiente llegará solo a `target`.

</details>

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
