# Preparación CodeSignal ICA — Dropbox (Infrastructure Software Engineer)

## El problema: In-Memory Cloud Storage

Vas a implementar un sistema de almacenamiento en la nube **en memoria** (nada se escribe a disco). Los requisitos llegan por niveles; cada nivel se construye sobre el anterior.

---

## Nivel 1 — Operaciones básicas de archivos

### Enunciado

Implementa:

- `add_file(name: str, size: int) -> bool`
  Agrega un archivo. Devuelve `True` si se agregó y `False` si ya existe un archivo con ese nombre (en ese caso no cambia nada).
- `get_file_size(name: str) -> int | None`
  Devuelve el tamaño del archivo, o `None` si no existe.
- `delete_file(name: str) -> int | None`
  Elimina el archivo y devuelve su tamaño, o `None` si no existía.

---

## Nivel 2 — Consultas: los archivos más grandes

### Enunciado

Implementa:

- `get_n_largest(prefix: str, n: int) -> list[str]`
  Devuelve los `n` archivos más grandes cuyo nombre **empieza** con `prefix`, en formato `"nombre(tamaño)"`.
  - Orden: tamaño **descendente**; si hay empate, nombre en orden **lexicográfico ascendente**.
  - Si hay menos de `n` coincidencias, devuelve todas. Si no hay ninguna (o `n` ≤ 0), devuelve `[]`.

Ejemplo: con `dir/a`(5), `dir/b`(20) y `dir/c`(10), `get_n_largest("dir/", 2)` → `["dir/b(20)", "dir/c(10)"]`.

---

## Nivel 3 — Usuarios con capacidad y fusión de cuentas

### Enunciado

Ahora los archivos tienen dueño.

- Existe desde el inicio un usuario `"admin"` con **capacidad ilimitada**. Todos los archivos creados con `add_file` (L1) pertenecen a `"admin"`.
- `add_user(user_id: str, capacity: int) -> bool`
  Crea un usuario con esa capacidad total (en bytes). `False` si el id ya existe (incluido `"admin"`).
- `add_file_by(user_id: str, name: str, size: int) -> int | None`
  Igual que `add_file`, pero el archivo pertenece a `user_id`. Devuelve la **capacidad restante** del usuario después de agregarlo.
  Devuelve `None` si el usuario no existe, si `user_id` es `"admin"`, si el nombre ya existe (de cualquier dueño) o si el archivo excede la capacidad restante.
- `delete_file` (de L1) ahora también **libera** la capacidad del dueño.
- `merge_user(target_id: str, source_id: str) -> int | None`
  Fusiona `source` dentro de `target`:
  - todos los archivos de `source` pasan a ser de `target`;
  - la capacidad de `target` aumenta en la capacidad **total** de `source`;
  - `source` deja de existir (su id puede volver a crearse después con `add_user`).

  Devuelve la capacidad restante de `target`. Devuelve `None` si los ids son iguales, si alguno no existe o si alguno es `"admin"`.

---

## Nivel 4 — Backup y restore por usuario

### Enunciado

- `backup_user(user_id: str) -> int | None`
  Guarda un snapshot de los archivos actuales del usuario (nombre y tamaño). Si ya existía un backup, **lo reemplaza**. Devuelve el número de archivos respaldados. `None` si el usuario no existe o es `"admin"`.
  Los cambios posteriores a los archivos **no afectan** al backup.
- `restore_user(user_id: str) -> int | None`
  1. Elimina **todos** los archivos que el usuario tiene actualmente.
  2. Si tiene backup, recrea cada archivo del backup con su tamaño original, **excepto** los que tengan un nombre que ahora usa otro usuario (esos se omiten).
  3. Devuelve el número de archivos restaurados (0 si no había backup). `None` si el usuario no existe o es `"admin"`.

  La capacidad del usuario no cambia con el restore.
- Ajuste a `merge_user`: el backup de `source` **se descarta**; el de `target` se queda como estaba.

---

## Bitácora

Copia este bloque por sesión.

```
### Sesión N — fecha
Nivel(es): 
Tiempo por nivel: L1 __ / L2 __ / L3 __ / L4 __
Tests: L1 _/7  L2 _/8  L3 _/14  L4 _/10
Hints abiertos: 
Dónde me atoré: 
Bug que más tiempo me costó: 
Refactor que me obligó el siguiente nivel (¿mi diseño anterior aguantó?): 
Qué haría distinto: 
```
