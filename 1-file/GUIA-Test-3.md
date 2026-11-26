# Preparación CodeSignal ICA — Dropbox (Infrastructure Software Engineer)

## El problema: In-Memory Cloud Storage

Vas a implementar un sistema de almacenamiento en la nube **en memoria** (nada se escribe a disco). Los requisitos llegan por niveles; cada nivel se construye sobre el anterior.

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

