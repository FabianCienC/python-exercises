# Práctica 5 — Por qué la solución está diseñada así

> Léelo después de intentar. El código está en `solucion_workers.txt`.

## Cómo se verificó

- Pasa los **30/30** tests.
- Se comparó contra una implementación "fuerza bruta" que calcula el salario **unidad por unidad de tiempo**, revisando en cada instante si cae en una sesión y en algún periodo doble. Es una forma de calcular completamente distinta. Con **3,000 secuencias aleatorias de 60 operaciones**, las respuestas coinciden en todas.

---

## 1. Guardar sesiones, no solo un total

```python
@dataclass
class Session:
    start: int
    end: int
    compensation: int
```

En el L1, `get` se resuelve con un contador. Pero el L3 pregunta cuánto se ganó **en un periodo**, y eso es imposible de reconstruir con un total. Con la lista de sesiones desde el L1, `calc_salary` es recorrerla.

La solución mantiene **ambas** cosas: la lista de sesiones (para preguntas sobre periodos) y contadores (`total_time`, `position_time`) para responder rápido lo frecuente. Es el mismo trade-off de la práctica 1 entre `used` y la lista de archivos.

## 2. La tarifa se congela en la sesión

`Session.compensation` guarda la tarifa vigente **cuando la sesión se cierra**. Así:
- un ascenso posterior no cambia lo que se pagó antes;
- `calc_salary` no necesita saber cuándo hubo ascensos: cada sesión ya trae su tarifa.

Es el patrón de **guardar el valor vigente en el momento del hecho**, igual que el cashback del banco se registraba con su `due`. La alternativa (guardar un historial de tarifas y buscar cuál aplicaba en cada momento) funciona, pero es más código y más bugs.

## 3. El ascenso es un evento pendiente que se aplica al entrar

```python
if w.entered_at is None:                       # entra
    if w.pending and w.pending.start <= timestamp:
        ... aplicar ...
        w.position_time = 0
```

- Se revisa **solo al entrar**: así, una sesión en curso conserva la tarifa vieja, y como la tarifa se congela al cerrar, todo cuadra.
- `pending` permite un solo ascenso a la vez: un segundo `promote` con uno pendiente es inválido.
- Al aplicarse, `position_time` vuelve a 0, porque el L3 cambia `top_n_workers` para que cuente solo el tiempo en el puesto actual. `total_time` no se toca: `get` sigue siendo el total.

Es otra versión de "ponerse al día": un evento con fecha que se dispara cuando el sistema lo observa. En el banco lo observaba cualquier método; aquí, solo la entrada del trabajador, porque el enunciado lo define así.

## 4. Intervalos semiabiertos y una sola fórmula

```python
def overlap(a1, b1, a2, b2):
    return max(0, min(b1, b2) - max(a1, a2))
```

Con intervalos `[inicio, fin)`, la intersección de dos intervalos es **una línea**, y no hay casos especiales: si no se tocan, `min - max` es negativo y el `max(0, ...)` lo vuelve 0. Es una fórmula que conviene saber de memoria.

## 5. Merge intervals para que el doble pago no se acumule

```python
for start, end in sorted(self._double_periods):
    if merged and start <= merged[-1][1]:
        merged[-1][1] = max(merged[-1][1], end)
    else:
        merged.append([start, end])
```

- Si sumaras la intersección con cada periodo doble por separado, un tramo cubierto por dos periodos se pagaría al triple. Por eso primero se **fusionan** en periodos disjuntos.
- Después, para cada sesión recortada `[a, b)`: `pago = (b - a + tiempo_doble) * tarifa`. Pagar el doble es pagar una vez más la parte doble.
- Se recalcula la fusión en cada `calc_salary`, porque un `set_double_paid` posterior es retroactivo. Con pocos periodos es lo más simple; si hubiera muchos, se podría cachear y recalcular solo cuando llega uno nuevo.

## Complejidades

| Operación | Tiempo |
|---|---|
| `add_worker`, `register`, `get`, `promote`, `set_double_paid` | O(1) |
| `top_n_workers` | O(W log W) |
| `calc_salary` | O(D log D + S · D), con S = sesiones y D = periodos dobles |

## Lo transferible a otros problemas

1. **Si te preguntan "en un periodo", guarda eventos con su inicio y fin**, no solo totales.
2. **Congela en cada registro el valor vigente** (tarifa, precio, puesto) para no reconstruir historiales.
3. **Intervalos `[a, b)` + `max(0, min - max)`** para cualquier intersección.
4. **Merge intervals** cuando los periodos pueden traslaparse y no deben contarse doble.
