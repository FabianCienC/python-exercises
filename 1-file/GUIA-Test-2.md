# Preparación CodeSignal ICA — Dropbox (Infrastructure Software Engineer)

## El problema: In-Memory Cloud Storage

Vas a implementar un sistema de almacenamiento en la nube **en memoria** (nada se escribe a disco). Los requisitos llegan por niveles; cada nivel se construye sobre el anterior.

---

## Nivel 2 — Consultas: los archivos más grandes

### Enunciado

Implementa:

- `get_n_largest(prefix: str, n: int) -> list[str]`
  Devuelve los `n` archivos más grandes cuyo nombre **empieza** con `prefix`, en formato `"nombre(tamaño)"`.
  - Orden: tamaño **descendente**; si hay empate, nombre en orden **lexicográfico ascendente**.
  - Si hay menos de `n` coincidencias, devuelve todas. Si no hay ninguna (o `n` ≤ 0), devuelve `[]`.

Ejemplo: con `dir/a`(5), `dir/b`(20) y `dir/c`(10), `get_n_largest("dir/", 2)` → `["dir/b(20)", "dir/c(10)"]`.

