# Preparación CodeSignal ICA — Dropbox (Infrastructure Software Engineer)

## El problema: In-Memory Cloud Storage

Vas a implementar un sistema de almacenamiento en la nube **en memoria** (nada se escribe a disco). Los requisitos llegan por niveles; cada nivel se construye sobre el anterior.

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
