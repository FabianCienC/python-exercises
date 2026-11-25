# Práctica 3 — Base de datos en memoria con TTL

## Objetivo

Practicar el otro gran clásico de la ICA: una base de datos tipo clave → campos → valor, con **expiración (TTL)** y **backup/restore** que respeta el tiempo de vida restante.

**Modo recomendado:** semi-simulacro. Abre un hint solo si llevas **más de 10 minutos atorado** y anota cuál.

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
| `db_inicio.txt` | Tu código (Python) |
| `test_db.txt` | Tests por nivel |
| `soluciones/` | Solución y explicación: **no abrir antes de tiempo** |

```bash
python test_db.txt db_inicio.txt --nivel 1
python test_db.txt db_inicio.txt --nivel 4 -v
```

## Medición

| Nivel | Objetivo | Tu tiempo | Tests | Hints |
|---|---|---|---|---|
| L1 | 10 min | | /7 | |
| L2 | 15 min | | /6 | |
| L3 | 25 min | | /8 | |
| L4 | 35 min | | /9 | |

---

## Reglas generales del problema

- La base guarda **registros**: cada registro tiene una `key` y varios `field`, cada uno con un `value` (strings).
- Todos los métodos reciben `timestamp`; los timestamps de llamadas sucesivas son **estrictamente crecientes**.
- Cuando se devuelve `False` o `None` por un error, **no se modifica nada**.

---

## Nivel 1 — Operaciones básicas

### Enunciado

- `set(timestamp, key, field, value) -> None`
  Guarda `value` en `field` del registro `key` (crea el registro si no existe; sobrescribe si el campo ya existía).
- `get(timestamp, key, field) -> str | None`
  Valor del campo, o `None` si el registro o el campo no existen.
- `delete(timestamp, key, field) -> bool`
  Borra el campo. `True` si existía, `False` si no. Si el registro se queda sin campos, deja de existir.
- `compare_and_set(timestamp, key, field, expected, new_value) -> bool`
  Si el campo existe y su valor actual es `expected`, lo cambia a `new_value` y devuelve `True`. Si no, `False` (y no crea nada).

### Subtareas

- [ ] Elige la estructura: dos niveles de búsqueda (llave y campo).
- [ ] Decide qué guardas por campo. ¿Solo el string o algo más?
- [ ] Implementa los 4 métodos.

### Checklist

- Borrar un campo no afecta a los otros del mismo registro.
- Un CAS fallido no crea el campo.

<details>
<summary>Hint 1</summary>

Otra vez todos los métodos reciben `timestamp` y hoy no lo usas. ¿Qué propiedad *temporal* podría tener un valor guardado en una base de datos?

</details>

<details>
<summary>Hint 2</summary>

`dict[str, dict[str, Entry]]`, donde `Entry` es una dataclass con `value` (y espacio para lo que venga). Un helper que diga si un campo "existe" en un momento dado te va a ahorrar mucho después.

</details>

---

## Nivel 2 — Scans

### Enunciado

- `scan(timestamp, key) -> list[str]`
  Todos los campos del registro en formato `"field(value)"`, ordenados por `field` ascendente. `[]` si el registro no existe.
- `scan_by_prefix(timestamp, key, prefix) -> list[str]`
  Igual, pero solo los campos cuyo nombre empieza con `prefix`.

### Subtareas

- [ ] Implementa `scan`.
- [ ] Reutilízalo (o su lógica) en `scan_by_prefix`.

### Checklist

- Registro inexistente → `[]` · campos borrados no aparecen · el prefijo filtra por **campo**, no por llave.

<details>
<summary>Hint 1</summary>

Un helper que devuelva los campos "válidos" de un registro ya ordenados te sirve para ambos métodos, y en el L3 solo tendrás que cambiar ese helper.

</details>

<details>
<summary>Hint 2</summary>

`sorted(self._data.get(key, {}).items())` ordena por nombre de campo; formatea con `f"{f}({e.value})"`.

</details>

---

## Nivel 3 — TTL (tiempo de vida)

### Enunciado

- `set_with_ttl(timestamp, key, field, value, ttl) -> None`
  Como `set`, pero el campo solo existe durante `[timestamp, timestamp + ttl)`. En `timestamp + ttl` ya expiró.
- Todas las operaciones anteriores deben tratar un campo expirado **como si no existiera**: `get` → `None`, `delete` → `False`, `compare_and_set` → `False`, y no aparece en los scans.
- `set` (sin TTL) sobre un campo crea un valor que **no expira**, aunque antes tuviera TTL.
- `compare_and_set` **conserva** la expiración que tuviera el campo.

### Subtareas

- [ ] Agrega la expiración a lo que guardas por campo.
- [ ] Centraliza la regla "¿está vivo en `ts`?" en un solo lugar.
- [ ] Revisa que **cada** método use esa regla.
- [ ] Ajusta `compare_and_set` para que no toque la expiración.

### Checklist

- Expira exactamente en `ts + ttl`.
- `set_with_ttl` sobre un campo con TTL reemplaza la expiración.
- Los scans excluyen los expirados.

<details>
<summary>Hint 1</summary>

No borres nada "cuando expira": no hay reloj. Guarda **cuándo** expira y pregunta al leer (expiración lazy). Si en L1–L2 todas las lecturas pasan por uno o dos helpers, este nivel es cambiar esos helpers.

</details>

<details>
<summary>Hint 2</summary>

- `Entry(value, expires_at=None)` con `alive(ts)`: `expires_at is None or ts < expires_at`.
- `set_with_ttl` → `Entry(value, timestamp + ttl)`; `set` → `Entry(value)`.
- En CAS, modifica `entry.value` en el objeto existente en vez de crear uno nuevo: así conservas `expires_at`.

</details>

---

## Nivel 4 — Backup y restore

### Enunciado

- `backup(timestamp) -> int`
  Guarda un snapshot de toda la base en ese momento (solo los campos vivos). Devuelve el número de **registros** (llaves) que tienen al menos un campo vivo. Se conservan **todos** los backups, no solo el último.
- `restore(timestamp, timestamp_to_restore) -> bool`
  Reemplaza toda la base por el backup **más reciente con tiempo ≤ `timestamp_to_restore`**. `False` si no existe ninguno (y no cambia nada).
  - **Recálculo del TTL:** si un campo tenía `R` milisegundos de vida restante al hacer el backup, después del restore vive hasta `timestamp + R`. Los campos sin TTL siguen sin expirar.
  - Los cambios posteriores al backup no deben afectar al snapshot guardado.

### Subtareas

- [ ] Decide qué guardar por campo en el snapshot (pista: no es lo mismo que guardas en la base viva).
- [ ] Guarda los backups de forma que encontrar "el último ≤ T" sea rápido.
- [ ] `backup`, cuidando que sea una copia independiente.
- [ ] `restore` con el recálculo de expiración.

### Checklist

- Restore sin backup válido → `False` y nada cambia.
- Varios backups: elige el correcto.
- Un CAS después del backup no altera el snapshot (¡cuidado con compartir objetos `Entry`!).
- Restaurar dos veces el mismo backup da el mismo estado.

<details>
<summary>Hint 1</summary>

Si guardas `expires_at` absoluto, al restaurar en el futuro todo estaría expirado. Guarda lo que **falta**. Y recuerda que el CAS del L3 modifica el objeto en sitio: si el snapshot apunta al mismo objeto, el CAS "viaja al pasado".

</details>

<details>
<summary>Hint 2</summary>

- Snapshot: `{key: {field: (value, restante_o_None)}}` con tuplas (valores, no objetos). `restante = expires_at - timestamp`.
- Listas paralelas `_backup_times` y `_backups`; como los timestamps crecen, `append` las mantiene ordenadas.
- `i = bisect.bisect_right(self._backup_times, timestamp_to_restore) - 1`.
- Al restaurar, crea objetos `Entry` **nuevos** con `expires_at = timestamp + restante`.

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
