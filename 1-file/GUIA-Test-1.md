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
