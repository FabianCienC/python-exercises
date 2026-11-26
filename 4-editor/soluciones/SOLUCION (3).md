# Práctica 4 — Por qué la solución está diseñada así

> Léelo después de intentar. El código está en `solucion_editor.txt`.

## Cómo se verificó

- Pasa los **33/33** tests.
- Se comparó contra una implementación "fuerza bruta" independiente, con **4,000 secuencias aleatorias de 60 operaciones** que mezclan inserts vacíos, selecciones invertidas, cursores fuera de rango, undo/redo y cambios de documento. Las respuestas coinciden en todas.

---

## 1. Todo el estado editable en un `Document` desde el L1

```python
@dataclass
class Document:
    text: str = ""
    cursor: int = 0
    selection: tuple[int, int] | None = None
    undo_stack: list[State] = field(default_factory=list)
    redo_stack: list[State] = field(default_factory=list)
```

El L4 está diseñado para castigar a quien guardó `self.text` y `self.cursor` como atributos sueltos del editor: al aparecer "varios documentos" hay que mover todo. Con `Document` desde el inicio, el L4 se reduce a:

```python
self._docs = {"default": Document()}
@property
def _doc(self): return self._docs[self._active]
```

Es la misma lección de siempre (la entidad como objeto), con un giro: aquí la entidad no es obvia en el L1, porque "el editor" parece ser la entidad. La pregunta que lo revela es: **¿podría haber más de uno de esto?**

## 2. Una sola operación de edición: reemplazar un rango

```python
def _replace(self, start, end, new):
    new_text = d.text[:start] + new + d.text[end:]
    d.cursor = start + len(new)
    d.selection = None
```

- `insert` sin selección → reemplaza `[cursor, cursor)` por el texto.
- `insert` con selección → reemplaza la selección.
- `backspace` → reemplaza `[cursor-1, cursor)` o la selección por `""`.
- `paste` → `insert(clipboard)`, literalmente.

Con esto:
- **L2 casi no cuesta:** la selección solo cambia *qué rango* se reemplaza (`target_range()`).
- **L3 se implementa en un solo lugar:** el historial se registra dentro de `_replace`, así que todas las ediciones quedan cubiertas sin tocar los métodos públicos.

## 3. Undo/redo con snapshots, no con operaciones inversas

Hay dos formas de hacer undo:
1. **Guardar la operación** ("inserté 'abc' en la posición 3") y programar su inversa. Hay que escribir una inversa por cada tipo de operación, y es fácil equivocarse con la selección.
2. **Guardar el estado anterior** (una foto) y volver a ella. **Esta es la que usa la solución.**

```python
State = tuple[str, int, tuple[int, int] | None]   # (texto, cursor, selección)
```

- Los strings y las tuplas son **inmutables**, así que la foto no puede cambiar después. Es la regla de los backups (valores, no referencias) llevada a su forma más simple.
- La foto se toma **antes** de modificar. Así `undo` restaura texto, cursor y selección, que es lo que piden los tests difíciles del L3.
- **Dos pilas:** `undo` mueve el estado actual a redo y restaura lo último de undo; `redo` es el espejo.
- **Una edición nueva vacía redo:** si deshaces y luego escribes, la "rama" deshecha ya no existe.
- **Solo se registran cambios reales** (`if changed`): un `backspace` en la posición 0 o un `paste` vacío no deben ocupar un lugar en el historial.

**Costo:** cada foto copia el texto (O(n) de memoria por edición). En el examen es perfectamente aceptable; en un editor real se guardarían diferencias.

## 4. Detalles que los tests ocultos suelen revisar

- **Ajuste de límites** con `max(0, min(pos, len(text)))`, tanto en `move_cursor` como en `select`.
- **`select` con `start > end`:** se intercambian. Con `start == end` se delega a `move_cursor`, sin duplicar lógica.
- **`copy` sin selección** no toca el portapapeles.
- **El portapapeles vive en el editor, no en el documento,** porque es compartido. Leer con cuidado qué estado es global y qué es por documento es parte de lo que evalúa el L4.
- **No se puede borrar el documento activo:** se valida antes de borrar.

## Complejidades

| Operación | Tiempo |
|---|---|
| `insert`, `backspace`, `paste` | O(n) por el slicing del string |
| `move_cursor`, `select`, `copy` | O(1) (copy: O(tamaño de la selección)) |
| `undo`, `redo` | O(1) |
| Documentos | O(1) |

## Lo transferible a otros problemas

1. **"¿Podría haber más de uno de esto?"** Si la respuesta es tal vez, conviértelo en objeto desde el L1.
2. **Reduce las operaciones a una primitiva** (aquí, reemplazar un rango) y haz que todo pase por ella.
3. **Undo/redo = dos pilas de snapshots inmutables.** Toma la foto antes de modificar y vacía redo en cada edición nueva.
