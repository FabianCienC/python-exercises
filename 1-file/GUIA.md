# Preparación CodeSignal ICA — Dropbox (Infrastructure Software Engineer)

## Objetivo

Llegar al examen sabiendo **descomponer un problema progresivo de 4 niveles y avanzar sin bloquearte**, no reconociendo un problema memorizado.

**Meta medible del simulacro final:** L1–L3 completos en ≤ 60 min, con L4 iniciado.

---

## Reglas de práctica (para que se parezca al examen)

1. **Sin IA ni autocompletado inteligente.** Usa un editor simple (IDLE, nano, o el entorno de práctica de CodeSignal). Puedes consultar la documentación oficial de Python, igual que en el examen.
2. **Cronómetro siempre corriendo.** Anota el tiempo al terminar cada nivel, aunque pares a la mitad.
3. **Las capas se abren en orden:** enunciado → subtareas → Hint 1 → Hint 2 → solución. Antes de abrir un hint, intenta al menos **5–10 minutos** con la capa anterior.
4. **Un solo archivo que crece.** No reescribas desde cero en cada nivel. Refactorizar lo que ya tienes *es* la habilidad que evalúan.
5. **Puedes parar cuando quieras.** Cada nivel es un buen punto de corte; al retomar, apunta en la bitácora dónde te quedaste.

---

## Archivos

| Archivo | Para qué |
|---|---|
| `GUIA.md` | Este documento: enunciados, subtareas, hints y bitácora |
| `cloud_storage_inicio.txt` | Esqueleto donde escribes tu código (es Python) |
| `test_cloud_storage.txt` | Tests por nivel: te dice cuántos casos pasas |
| `solucion_cloud_storage.txt` | Solución de referencia — **no la abras antes de tiempo** |
| `SOLUCION.md` | Por qué la solución está diseñada así |

**Correr tests** (Python ejecuta archivos `.txt` sin problema):

```bash
python test_cloud_storage.txt cloud_storage_inicio.txt --nivel 1
python test_cloud_storage.txt cloud_storage_inicio.txt --nivel 2 -v   # -v muestra el detalle de cada fallo
```

> En CodeSignal **no ves todos los tests**: algunos son ocultos. Por eso, antes de correr los tests, piensa tú los casos borde (la checklist de cada nivel te ayuda).

---

## Cómo medir tu avance

| Nivel | Tiempo objetivo | Tu tiempo | Tests | ¿Abriste hints? |
|---|---|---|---|---|
| L1 | 10 min | | /7 | |
| L2 | 20 min | | /8 | |
| L3 | 30 min | | /14 | |
| L4 | 30 min | | /10 | |

La primera vuelta (guiada) **no** se mide contra el tiempo objetivo: mide cuánto te tardas y aprende. La segunda vuelta (desde cero, sin hints) sí.

---

## El problema: In-Memory Cloud Storage

Vas a implementar un sistema de almacenamiento en la nube **en memoria** (nada se escribe a disco). Los requisitos llegan por niveles; cada nivel se construye sobre el anterior.

Reglas generales para todos los niveles:

- Los nombres de archivo son **globalmente únicos** (no hay carpetas reales; `"img/a.png"` es solo un string).
- Los tamaños son enteros ≥ 0.
- Cuando el enunciado dice que se devuelve `None`, **la operación no debe modificar nada**.

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

### Subtareas

- [ ] Decide **qué estructura** guarda los archivos. Pregúntate: ¿cómo busco un archivo por nombre en O(1)?
- [ ] Implementa `add_file` con el caso de duplicado.
- [ ] Implementa `get_file_size`.
- [ ] Implementa `delete_file`.
- [ ] Corre `--nivel 1`.

### Checklist de casos borde

- ¿Agregar un nombre duplicado deja intacto el tamaño original?
- ¿Se puede volver a agregar un nombre después de borrarlo?

<details>
<summary>Hint 1 (conceptual)</summary>

Un diccionario resuelve todo el nivel. La decisión importante no es *esa*: es **qué guardas como valor**. Lee los títulos de los niveles 3 y 4 de esta guía (solo los títulos) y pregúntate qué información más va a necesitar un archivo en el futuro.

</details>

<details>
<summary>Hint 2 (concreto)</summary>

En vez de `files[name] = size`, guarda un objeto (una `dataclass` o un dict) con `size` y un campo para el **dueño**. Hoy el dueño siempre es el mismo, pero en L3 cambia, y agregar un campo es mucho más barato que cambiar el tipo de lo que guardas.

</details>

---

## Nivel 2 — Consultas: los archivos más grandes

### Enunciado

Implementa:

- `get_n_largest(prefix: str, n: int) -> list[str]`
  Devuelve los `n` archivos más grandes cuyo nombre **empieza** con `prefix`, en formato `"nombre(tamaño)"`.
  - Orden: tamaño **descendente**; si hay empate, nombre en orden **lexicográfico ascendente**.
  - Si hay menos de `n` coincidencias, devuelve todas. Si no hay ninguna (o `n` ≤ 0), devuelve `[]`.

Ejemplo: con `dir/a`(5), `dir/b`(20) y `dir/c`(10), `get_n_largest("dir/", 2)` → `["dir/b(20)", "dir/c(10)"]`.

### Subtareas

- [ ] Filtra los archivos por prefijo.
- [ ] Ordena con el criterio doble (tamaño desc, nombre asc).
- [ ] Recorta a `n` y formatea.
- [ ] Corre `--nivel 2` (y confirma que L1 sigue pasando).

### Checklist de casos borde

- Empates de tamaño · prefijo vacío `""` · `n` mayor que el número de archivos · `n = 0` · archivos borrados no aparecen.

<details>
<summary>Hint 1 (conceptual)</summary>

Para ordenar por dos criterios con direcciones opuestas no necesitas dos `sort`: basta una **clave** que sea una tupla. ¿Cómo conviertes "más grande primero" en "más chico primero" para un número?

</details>

<details>
<summary>Hint 2 (concreto)</summary>

`sorted(candidatos, key=lambda f: (-f.size, f.name))[:n]`. Para el filtro, `str.startswith(prefix)`. Opcional: `heapq.nsmallest(n, candidatos, key=...)` hace lo mismo sin ordenar todo.

</details>

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

### Subtareas

- [ ] Modela al usuario: ¿qué necesitas saber de él para responder "capacidad restante" rápido?
- [ ] Crea `"admin"` en el constructor y haz que `add_file` le asigne los archivos.
- [ ] Implementa `add_user` y `add_file_by` (valida primero, modifica después).
- [ ] Actualiza `delete_file` para liberar capacidad.
- [ ] Implementa `merge_user`.
- [ ] Corre `--nivel 3` y confirma que L1–L2 siguen pasando.

### Checklist de casos borde

- Archivo de tamaño exactamente igual a la capacidad restante (debe entrar y devolver 0).
- Un `add_file_by` fallido **no** deja el archivo creado.
- Después de un merge, borrar un archivo que era de `source` libera capacidad de `target`.
- Un merge inválido no modifica nada.

<details>
<summary>Hint 1 (conceptual)</summary>

Vas a tener **dos vistas** de los mismos datos: archivos por nombre y archivos por usuario. Esto pasa mucho en sistemas reales (piensa en un índice de base de datos). El riesgo es que se desincronicen; la defensa es que **solo una o dos funciones** puedan modificarlas.

</details>

<details>
<summary>Hint 2 (concreto)</summary>

- `User` con `capacity`, `used` y `files: set[str]`. Restante = `capacity - used` (no recalcules sumando cada vez).
- Para admin, `capacity = None` significa ilimitada.
- Escribe dos helpers privados: `_attach(name, size, owner)` (crea el archivo y actualiza `used` y `files` del dueño) y `_detach(name)` (lo inverso). `add_file`, `add_file_by` y `delete_file` los usan **todos**.
- En `merge_user` no necesitas borrar y volver a crear archivos: solo cambia el dueño y suma `used`, `capacity` y `files`.

</details>

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

### Subtareas

- [ ] Decide dónde y cómo guardar los backups (¿por qué **no** sirve guardar una referencia al `set` de archivos del usuario?).
- [ ] Implementa `backup_user`.
- [ ] Implementa `restore_user` reutilizando tus helpers de L3.
- [ ] Ajusta `merge_user`.
- [ ] Corre `--nivel 4` y confirma L1–L3.

### Checklist de casos borde

- Restore sin backup → borra todo y devuelve 0.
- Restore dos veces seguidas → mismo resultado.
- Backup, luego borrar un archivo y crear otro con el **mismo nombre** y otro tamaño → el restore vuelve al tamaño original.
- Restore tras un merge en `target`: también se borran los archivos que llegaron del merge.
- Capacidad usada correcta después del restore.

<details>
<summary>Hint 1 (conceptual)</summary>

Un backup debe ser una **copia de valores**, no una referencia a objetos vivos. Si guardas los objetos `File` o el `set` del usuario, cualquier cambio posterior "viaja en el tiempo" hacia tu backup. Y si tus helpers de L3 están bien, el restore es básicamente "detach de todo + attach de lo respaldado".

</details>

<details>
<summary>Hint 2 (concreto)</summary>

- `self._backups: dict[str, dict[str, int]]` → `user_id -> {nombre: tamaño}`.
- Al iterar los archivos del usuario para borrarlos, itera sobre `list(user.files)`: modificar un `set` mientras lo recorres lanza error.
- Para el conflicto de nombres: si `name in self._files` después de borrar los del usuario, ese nombre es de otro → `continue`.
- En `merge_user`: `self._backups.pop(source_id, None)`.

</details>

---

## Después de la vuelta guiada

1. Compara tu código con `solucion_cloud_storage.txt` y lee `SOLUCION.md`. Anota en la bitácora 2–3 diferencias de diseño.
2. **Segunda vuelta:** archivo nuevo vacío, 90 min, sin abrir esta guía más allá de los enunciados. Aquí sí mides contra el tiempo objetivo.
3. **Fase 2 — simulacros:** cuando estés listo, pídeme un problema **de otro dominio** (p. ej. banco con transferencias programadas, o base de datos con TTL), sin hints, para medir si lo aprendido se transfiere.

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
