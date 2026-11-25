# Práctica 2 — Por qué la solución está diseñada así

> Léelo después de intentar. El código está en `solucion_banco.txt`.

## Cómo se verificó

- Pasa los **30/30** tests.
- Se comparó contra una implementación "fuerza bruta" independiente, que guarda un log de movimientos y recalcula saldos sumando todo, con **1,500 secuencias aleatorias de 60 operaciones**. Incluye saltos de 12 y 24 horas para que venzan cashbacks entre operaciones. Las respuestas coinciden en todas.

---

## 1. Un solo helper para cambiar saldos (la decisión del L1 que define el L4)

```python
def _change_balance(self, account, delta, ts):
    account.balance += delta
    account.record(ts)
```

Depósitos, transferencias (salida y entrada), pagos, cashbacks y merges pasan por aquí. En el L1 solo hacía `balance += delta`. Cuando el L4 pide el saldo histórico, basta con agregar `record(ts)` en **un** lugar, y todo el historial queda correcto.

Sin este helper, el L4 obliga a buscar cada `balance +=` repartido en seis métodos, y es fácil olvidar uno (normalmente el cashback). Es el mismo principio que `_attach` y `_detach` en la práctica 1: **la entidad central se modifica desde un solo punto**.

## 2. Eventos programados: heap + "ponerse al día" al inicio

```python
def _process_due(self, ts):
    while self._pending and self._pending[0][0] <= ts:
        due, _, payment_id = heapq.heappop(self._pending)
        ...
```

- **No hay reloj:** el sistema solo se ejecuta cuando alguien llama un método. Por eso cada método público empieza con `self._process_due(timestamp)`, incluidos `create_account` y `top_spenders`. Olvidarlo en uno solo es el bug #1 de este tipo de problemas: el test pasa en el método que revisaste y falla en el que no.
- **Heap con `(due, número, id)`:** `heappop` siempre da el que vence primero, en O(log n). El número de pago desempata en orden de creación y evita que Python compare objetos.
- **`<=` y no `<`:** un cashback que vence en `T` debe estar disponible para la operación en `T`.
- **Se registra con `due`, no con `ts`:** si la siguiente operación ocurre tres días después, el cashback llegó en su momento real. Así `get_balance` responde bien para cualquier instante intermedio. Y como `_process_due` corre antes de cada operación, el historial sigue ordenado por tiempo.

## 3. El pago sabe de quién es

`Payment.account_id` es la fuente de verdad del dueño:
- `get_payment_status` valida que el pago pertenezca a esa cuenta.
- Al vencer, el cashback se acredita a `payment.account_id`, **leído en ese momento**.

Gracias a eso, en el merge no hay que tocar el heap: se reasigna `account_id` de los pagos de `source` y los cashbacks pendientes llegan solos a `target`. Por eso cada cuenta guarda el `set` de sus pagos: para encontrarlos en O(pagos de la cuenta) sin recorrer todos.

## 4. Historial con listas paralelas + `bisect`

```python
i = bisect.bisect_right(self.history_ts, time_at) - 1
return self.history_bal[i] if i >= 0 else None
```

- Los timestamps llegan crecientes, así que `append` mantiene la lista ordenada sin hacer nada extra.
- `bisect_right(...) - 1` da "el último registro con tiempo ≤ `time_at`", incluidas las operaciones de ese mismo instante.
- **Un registro por timestamp:** si el mismo `ts` tiene varios cambios (cashback y operación, o las dos patas de un merge), se sobrescribe el último. El saldo "en `T`" es el final de `T`.
- `create_account` registra el saldo 0: consultar antes de la creación devuelve `None` (`i < 0`) y justo en la creación devuelve 0.
- Una cuenta re-creada tras un merge es un objeto **nuevo** con historial vacío, así que no hereda nada por accidente.

## 5. Dinero en enteros

`amount * CASHBACK_PERCENT // 100`: aritmética entera con piso, sin floats. Las constantes con nombre (`CASHBACK_DELAY`, `CASHBACK_PERCENT`) evitan números mágicos y errores al teclear `86400000`.

## 6. Validar antes de mover dinero

`transfer` valida misma cuenta, existencia de ambas y saldo suficiente, y **después** hace los dos `_change_balance`. Un `None` nunca deja medio movimiento. Lo mismo en `pay` y `merge_accounts`.

## Complejidades

| Operación | Tiempo |
|---|---|
| `create_account`, `deposit`, `transfer`, `pay`, `get_payment_status` | O(1) + O(k log P) por los k cashbacks vencidos |
| `top_spenders` | O(A log A) |
| `merge_accounts` | O(pagos de source) |
| `get_balance` | O(log H) |

## Lo transferible a otros problemas

1. **`timestamp` en todos los métodos desde el L1** = prepárate para historial o eventos.
2. **Eventos futuros** → heap + `_process_due(ts)` en la primera línea de cada método público.
3. **"¿Cuánto valía en T?"** → historial append-only + `bisect_right - 1`.
4. **Entidades que se fusionan** → que los objetos hijos (pagos) apunten a su dueño, y reasigna ese puntero.
