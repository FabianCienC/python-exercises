# Por qué la solución está diseñada así

> Léelo **después** de intentar los niveles. El código está en `solucion_cloud_storage.txt`.

## Cómo se verificó

- Pasa los **39/39** tests de `test_cloud_storage.txt`.
- Se comparó contra una implementación "fuerza bruta" independiente (recalcula todo desde cero en cada operación) con **3,000 secuencias aleatorias de 80 operaciones**. Las respuestas coinciden en todas.

Sobre el "600/600": en la ICA el puntaje sale de **cuántos tests (visibles y ocultos) pasas por nivel**, y los niveles altos pesan más. No hay puntos extra por estilo. Lo que hace que un buen diseño valga puntos es indirecto: te deja llegar al L4 a tiempo y sin bugs. Esta solución está pensada para eso.

---

## 1. El modelo de datos se decide en L1 pensando en L3–L4

```python
@dataclass
class File:  name, size, owner
@dataclass
class User:  user_id, capacity, used, files: set[str]
```

- Desde L1 cada archivo tiene `owner`, aunque hasta L3 siempre sea `"admin"`. Cuando llega L3 no hay que cambiar el tipo de lo que guarda el diccionario, solo empezar a usar el campo.
- `"admin"` es un `User` normal con `capacity=None`. Así `add_file` y `add_file_by` comparten el mismo camino de código, sin `if` especiales repartidos por todos lados.

**El error típico:** guardar `files[name] = size` en L1. En L3 te obliga a reescribir todo L1 y L2 con el reloj corriendo.

## 2. Dos índices, un solo punto de mutación

Hay dos vistas de los mismos datos:

- `_files: dict[nombre, File]`: búsqueda global por nombre, unicidad y `get_n_largest`.
- `User.files: set[nombre]` + `User.used`: "¿qué tiene este usuario?" y "¿cuánto le queda?" en O(1).

Dos estructuras pueden desincronizarse. La defensa son **invariantes** y **un solo lugar que los mantiene**:

> Invariante A: todo archivo en `_files` aparece en el `files` de exactamente un usuario, y ese usuario es `file.owner`.
> Invariante B: `user.used == sum(size de user.files)`.

Solo `_attach` y `_detach` tocan `_files`, `used` y `files` juntos. Todas las operaciones públicas (`add_file`, `add_file_by`, `delete_file`, `restore_user`) los usan, así que si esos dos helpers son correctos, todo lo demás lo es. `merge_user` es la única excepción consciente, porque no crea ni borra archivos: solo los reasigna, y por eso suma `used` y `capacity` directamente.

Es el mismo principio que usas en arquitectura: **una sola fuente de verdad para cada mutación**.

## 3. Validar todo antes de modificar nada

```python
if user is None or name in self._files or not user.can_fit(size):
    return None
self._attach(...)
```

Cuando el enunciado dice "devuelve `None`", los tests ocultos suelen verificar que **no quedó rastro**: un archivo a medio crear o una capacidad descontada. Primero se valida todo y después se hace una sola mutación. En `merge_user` igual: se verifican ids iguales, existencia y admin antes de mover un solo archivo.

## 4. Capacidad restante en O(1)

`used` se mantiene incrementalmente en `_attach` y `_detach`, en vez de sumar tamaños en cada `add_file_by`. Con pocos archivos daría igual, pero los tests de CodeSignal a veces traen casos grandes con límite de tiempo, y recalcular convierte O(1) en O(F) por operación.

## 5. `get_n_largest`: una clave de orden, no dos sorts

```python
heapq.nsmallest(n, candidates, key=lambda f: (-f.size, f.name))
```

- La tupla `(-size, name)` expresa "tamaño desc, nombre asc" en una sola clave.
- `nsmallest` mantiene un heap de tamaño `n`: O(F log n) en vez de O(F log F). `sorted(...)[:n]` también es totalmente válido en el examen y es más fácil de escribir bajo presión.
- `n <= 0` se maneja explícitamente: es un caso borde típico de los tests ocultos.

## 6. Backups como copia de valores

```python
self._backups[user_id] = {name: self._files[name].size for name in user.files}
```

- Se guarda `nombre → tamaño` (ints y strings, inmutables), **no** el `set` del usuario ni los objetos `File`. Si guardaras `user.files`, el backup cambiaría cada vez que el usuario agregue o borre algo. Ese bug es silencioso y solo lo detectan los tests ocultos.
- Un dict por usuario porque el enunciado pide "el último backup", no un historial. Si un nivel pidiera *restore a un timestamp*, se cambiaría a una lista de `(timestamp, snapshot)` con búsqueda binaria: el diseño lo permite sin tocar lo demás.

## 7. Restore = detach de todo + attach de lo respaldado

```python
for name in list(user.files):   # list(): copia para no mutar el set mientras se itera
    self._detach(name)
for name, size in sorted(backup.items()):
    if name in self._files: continue   # nombre de otro usuario
    self._attach(name, size, user_id)
```

Aquí se cobra la inversión de L3: el restore no tiene lógica propia de capacidad ni de índices, solo reutiliza los helpers. Por eso `used` queda bien automáticamente. Y no hace falta revisar la capacidad: el backup cupo cuando se tomó y la capacidad solo puede crecer (vía merge), así que siempre cabe.

`sorted(...)` no cambia el resultado (dentro de un backup no hay conflictos entre sí), pero hace la ejecución determinista, lo que facilita depurar.

## Complejidades

| Operación | Tiempo |
|---|---|
| `add_file`, `get_file_size`, `delete_file`, `add_user`, `add_file_by` | O(1) |
| `get_n_largest` | O(F log n) |
| `merge_user` | O(archivos de source) |
| `backup_user` | O(archivos del usuario) |
| `restore_user` | O(archivos actuales + archivos del backup · log) |

## Estrategia para el examen real

1. **Lee los 4 niveles si puedes; si no, lee el L1 con calma** y modela pensando en que habrá dueños, tiempo o historial. Casi todos los problemas ICA siguen la progresión CRUD → consultas/orden → entidades relacionadas o tiempo → snapshots/historial.
2. **Helpers de mutación desde el principio**: cuestan 2 minutos en L1 y ahorran 15 en L3–L4.
3. **Envía al pasar cada nivel.** La plataforma se queda con tu mejor corrida.
4. **Si un test falla y no ves por qué**, revisa en este orden: (a) ¿un caso de `None` modificó algo? (b) ¿el orden de empates? (c) ¿mutas una colección mientras la recorres? (d) ¿un backup comparte referencias?
5. **Nombres claros y loops simples** antes que comprehensions ingeniosas: bajo presión, el código legible es el que depuras rápido.
