"""
SOLUCIÓN DE REFERENCIA — In-Memory Cloud Storage (L1–L4)

No abras este archivo hasta haber intentado el nivel correspondiente.
Para correr los tests contra esta solución:
    python test_cloud_storage.txt solucion_cloud_storage.txt

Ideas clave (explicadas a detalle en SOLUCION.md):
  1. Modelo de datos completo desde L1: cada archivo sabe su tamaño y su dueño.
  2. Dos índices: archivos por nombre (global) y archivos por usuario.
  3. Un solo punto de mutación (_attach / _detach) que mantiene los invariantes:
       - todo archivo pertenece a exactamente un usuario
       - user.used == suma de tamaños de user.files
  4. Validar TODO antes de modificar NADA (sin estados a medias).
  5. Los backups son copias de valores (nombre -> tamaño), nunca referencias.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field

ADMIN_ID = "admin"


@dataclass
class File:
    name: str
    size: int
    owner: str


@dataclass
class User:
    user_id: str
    capacity: int | None          # None = capacidad ilimitada (solo admin)
    used: int = 0
    files: set[str] = field(default_factory=set)

    @property
    def remaining(self) -> int | None:
        if self.capacity is None:
            return None
        return self.capacity - self.used

    def can_fit(self, size: int) -> bool:
        return self.capacity is None or self.used + size <= self.capacity


class CloudStorage:
    def __init__(self) -> None:
        self._files: dict[str, File] = {}                      # nombre -> File
        self._users: dict[str, User] = {ADMIN_ID: User(ADMIN_ID, None)}
        self._backups: dict[str, dict[str, int]] = {}          # user -> {nombre: tamaño}

    # ------------------------------------------------------------------
    # Helpers internos: ÚNICOS lugares que modifican archivos/usuarios.
    # Si los invariantes se mantienen aquí, se mantienen en todo el sistema.
    # ------------------------------------------------------------------
    def _attach(self, name: str, size: int, owner_id: str) -> None:
        """Crea el archivo y lo asigna a su dueño (asume validación previa)."""
        owner = self._users[owner_id]
        self._files[name] = File(name, size, owner_id)
        owner.files.add(name)
        owner.used += size

    def _detach(self, name: str) -> File:
        """Elimina el archivo y libera la capacidad de su dueño."""
        file = self._files.pop(name)
        owner = self._users[file.owner]
        owner.files.discard(name)
        owner.used -= file.size
        return file

    def _regular_user(self, user_id: str) -> User | None:
        """Usuario creado con add_user (admin no cuenta para L3/L4)."""
        if user_id == ADMIN_ID:
            return None
        return self._users.get(user_id)

    # ------------------------------------------------------------------
    # Nivel 1
    # ------------------------------------------------------------------
    def add_file(self, name: str, size: int) -> bool:
        if name in self._files:
            return False
        self._attach(name, size, ADMIN_ID)
        return True

    def get_file_size(self, name: str) -> int | None:
        file = self._files.get(name)
        return file.size if file else None

    def delete_file(self, name: str) -> int | None:
        if name not in self._files:
            return None
        return self._detach(name).size

    # ------------------------------------------------------------------
    # Nivel 2
    # ------------------------------------------------------------------
    def get_n_largest(self, prefix: str, n: int) -> list[str]:
        if n <= 0:
            return []
        candidates = (f for f in self._files.values() if f.name.startswith(prefix))
        # Orden: tamaño descendente, luego nombre ascendente.
        # nsmallest con clave (-size, name) = top-n en O(F log n).
        top = heapq.nsmallest(n, candidates, key=lambda f: (-f.size, f.name))
        return [f"{f.name}({f.size})" for f in top]

    # ------------------------------------------------------------------
    # Nivel 3
    # ------------------------------------------------------------------
    def add_user(self, user_id: str, capacity: int) -> bool:
        if user_id in self._users:
            return False
        self._users[user_id] = User(user_id, capacity)
        return True

    def add_file_by(self, user_id: str, name: str, size: int) -> int | None:
        user = self._regular_user(user_id)
        if user is None or name in self._files or not user.can_fit(size):
            return None
        self._attach(name, size, user_id)
        return user.remaining

    def merge_user(self, target_id: str, source_id: str) -> int | None:
        if target_id == source_id:
            return None
        target = self._regular_user(target_id)
        source = self._regular_user(source_id)
        if target is None or source is None:
            return None

        # Transferir propiedad: el tamaño total no cambia, solo el dueño.
        for name in source.files:
            self._files[name].owner = target_id
        target.files |= source.files
        target.used += source.used
        target.capacity += source.capacity

        del self._users[source_id]
        self._backups.pop(source_id, None)   # L4: el backup del origen se descarta
        return target.remaining

    # ------------------------------------------------------------------
    # Nivel 4
    # ------------------------------------------------------------------
    def backup_user(self, user_id: str) -> int | None:
        user = self._regular_user(user_id)
        if user is None:
            return None
        # Copia de VALORES: cambios posteriores no afectan el backup.
        self._backups[user_id] = {name: self._files[name].size for name in user.files}
        return len(user.files)

    def restore_user(self, user_id: str) -> int | None:
        user = self._regular_user(user_id)
        if user is None:
            return None

        for name in list(user.files):        # list(): no mutar el set mientras se itera
            self._detach(name)

        restored = 0
        for name, size in sorted(self._backups.get(user_id, {}).items()):
            if name in self._files:          # nombre ocupado por otro usuario -> se omite
                continue
            self._attach(name, size, user_id)
            restored += 1
        return restored
