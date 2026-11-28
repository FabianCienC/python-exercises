"""
Tu código va aquí. Empieza solo con el Nivel 1.
Cuando pases el nivel, agrega los métodos del siguiente directamente en esta clase
(así funciona en CodeSignal: un solo archivo que va creciendo).

Correr tests:
    python test_cloud_storage.txt cloud_storage_inicio.txt --nivel 1
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class File:
    name: str
    size: int
    owner: str

@dataclass
class User:
    user_id: str
    capacity: int | None
    used: int = 0
    files: set[str] = field(default_factory=set)

    @property
    def remaining(self):
        return self.capacity - self.used

    def can_fit(self, size) -> bool:
        return self.capacity is None or self.used + size <= self.capacity


ADMIN_ID = "admin"

class CloudStorage:
    def __init__(self) -> None:
        self._files: dict[str, File] = {}
        self._users: dict[str, User] = {ADMIN_ID: User(ADMIN_ID, None)}
        self._backups: dict[str, dict[str, int]] = {}

    def _add_file(self, name: str, size: int, owner_id: str) -> None:
        owner = self._users[owner_id]
        self._files[name] = File(name, size, owner_id)
        owner.used += size
        owner.files.add(name)

    def _delete_file(self, name: str) -> File:
        file = self._files.pop(name)
        owner = self._users[file.owner]
        owner.used -= file.size
        owner.files.discard(name)
        return file
    
    # ---------------- Nivel 1 ----------------
    def add_file(self, name: str, size: int) -> bool:
        if name in self._files:
            return False
        self._add_file(name, size, ADMIN_ID)
        return True

    def get_file_size(self, name: str) -> int | None:
        file = self._files.get(name)
        return file.size if file else None

    def delete_file(self, name: str) -> int | None:
        if name not in self._files:
            return None
        return self._delete_file(name).size

    # ---------------- Nivel 2 ----------------
    def get_n_largest(self, prefix: str, n: int) -> list[str]:
        if n <= 0:
            return []
        files = [f for f in self._files.values() if f.name.startswith(prefix)]
        sorted_files = sorted(files, key=lambda f: (-f.size, f.name))[:n]
        return [f"{f.name}({f.size})" for f in sorted_files]

    # ---------------- Nivel 3 ----------------
    def add_user(self, user_id: str, capacity: int) -> bool:
        if user_id in self._users:
            return False
        self._users[user_id] = User(user_id, capacity)
        return True

    def add_file_by(self, user_id: str, name: str, size: int) -> int | None:
        if user_id not in self._users or user_id == ADMIN_ID:
            return None
        if name in self._files:
            return None
        user = self._users[user_id]
        if not user.can_fit(size):
            return None
        self._add_file(name, size, user_id)
        return user.remaining
        

    def merge_user(self, target_id: str, source_id: str) -> int | None:
        if ADMIN_ID in (target_id, source_id) or target_id == source_id:
            return None
        target = self._users.get(target_id)
        source = self._users.get(source_id)
        if target is None or source is None:
            return None
        
        target.files.update(source.files)

        for name in source.files:
            self._files[name].owner = target_id

        target.capacity += source.capacity
        target.used += source.used

        del self._users[source_id]
        self._backups.pop(source_id, None)
        return target.remaining

    # ---------------- Nivel 4 ----------------
    def backup_user(self, user_id: str) -> int | None:
        if user_id not in self._users or user_id == ADMIN_ID:
            return None
        user = self._users[user_id]
        self._backups[user_id] = {name: self._files[name].size for name in user.files}
        return len(user.files)

    def restore_user(self, user_id: str) -> int | None:
        if user_id not in self._users or user_id == ADMIN_ID:
            return None
        user = self._users[user_id]
        
        for name in list(user.files):
            self._delete_file(name)

        restored = 0
        for name, size in self._backups.get(user_id, {}).items():
            if name in self._files:
                continue
            self._add_file(name, size, user_id)
            restored += 1
        return restored