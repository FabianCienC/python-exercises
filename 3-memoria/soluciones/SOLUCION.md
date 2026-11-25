# Práctica 3 — Por qué la solución está diseñada así

> Léelo después de intentar. El código está en `solucion_db.txt`.

## Cómo se verificó

- Pasa los **30/30** tests.
- Se comparó contra una implementación "fuerza bruta" independiente, con un diccionario plano `(key, field) → [valor, expiración]` y backups que guardan la expiración absoluta y la convierten al restaurar, con **3,000 secuencias aleatorias de 70 operaciones**. Las respuestas coinciden en todas.

---

## 1. `Entry` desde el L1, aunque solo guarde un string

```python
@dataclass
class Entry:
    value: str
    expires_at: int | None = None
```

En el L1, `dict[key][field] = "valor"` funciona. Pero en el L3 cada campo necesita una expiración, y cambiar `str` por un objeto obliga a reescribir todos los métodos. Con `Entry` desde el inicio, el L3 es agregar un campo con default `None`. Es la misma lección de la práctica 1 (guardar objetos, no valores sueltos), ahora con el tiempo como dimensión extra.

## 2. Expiración lazy en un solo lugar

```python
def _get_alive(self, ts, key, field):
    entry = self._data.get(key, {}).get(field)
    if entry is None or not entry.alive(ts):
        return None
    return entry
```

- **Lazy:** nada se borra "cuando expira", porque no hay reloj. Se guarda *cuándo* expira y cada lectura pregunta.
- **Un solo lugar:** `get`, `delete` y `compare_and_set` usan `_get_alive`, y los scans usan `_alive_fields`. Si la regla cambiara (por ejemplo, `<=` en vez de `<`), se corrige en `Entry.alive` y listo. El bug típico es que `get` respete el TTL pero `scan` o `delete` no.
- **`ts < expires_at`:** el campo vive en `[ts, ts + ttl)`. En `ts + ttl` exacto ya expiró.

## 3. `compare_and_set` modifica en sitio

```python
entry.value = new_value
```

Cambiar el valor del objeto existente conserva `expires_at` automáticamente, que es lo que pide el L3. Crear un `Entry` nuevo lo perdería.

Esa misma decisión es la trampa del L4: si el snapshot guardara el **mismo** objeto `Entry`, un CAS posterior modificaría el backup. Por eso el snapshot guarda tuplas (valores), nunca objetos vivos.

## 4. Helpers de escritura: `_put` y `_remove`

`_remove` borra el campo y, si el registro se queda vacío, borra la llave. Así nunca quedan llaves vacías que harían que `backup()` contara registros sin campos. `_put` usa `setdefault` para crear el registro si no existe.

## 5. Backups: TTL restante, no absoluto

```python
(e.value, None if e.expires_at is None else e.expires_at - timestamp)
```

Es la trampa más famosa de este problema. Si guardas `expires_at` absoluto (por ejemplo, 30) y restauras en `t = 100`, todo aparece expirado. Lo correcto es guardar lo que **falta** (`30 - 20 = 10`) y al restaurar hacer `expires_at = 100 + 10`.

Además:
- Solo entran campos **vivos** al momento del backup, y las llaves sin campos vivos no se guardan. El conteo devuelto es `len(snapshot)`.
- El restore crea objetos `Entry` **nuevos**. Restaurar dos veces el mismo backup da el mismo resultado, porque el snapshot nunca se modifica.

## 6. Varios backups + `bisect`

```python
i = bisect.bisect_right(self._backup_times, timestamp_to_restore) - 1
```

Como los timestamps crecen, `append` mantiene `_backup_times` ordenada, y "el último backup con tiempo ≤ T" es una búsqueda binaria. Es el mismo patrón que `get_balance` en la práctica 2. Si `i < 0`, no hay backup válido: se devuelve `False` **antes** de tocar `self._data`.

## Complejidades

| Operación | Tiempo |
|---|---|
| `set`, `get`, `delete`, `compare_and_set`, `set_with_ttl` | O(1) |
| `scan`, `scan_by_prefix` | O(F log F), F = campos del registro |
| `backup` | O(total de campos) |
| `restore` | O(log B + campos del backup) |

## Lo transferible a otros problemas

1. **TTL** → guarda `expires_at`, verifica al leer y centraliza `alive(ts)`.
2. **Snapshots con tiempo** → guarda duraciones *relativas* y recalcúlalas al restaurar.
3. **Mutar en sitio + snapshots** → los snapshots guardan valores, nunca los objetos que mutas.
4. **"El último X con tiempo ≤ T"** → lista ordenada + `bisect_right - 1`. Sale en casi todos los L4 con tiempo.
