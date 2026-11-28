"""
Tu código va aquí. Empieza solo con el Nivel 1.
Cuando pases el nivel, agrega los métodos del siguiente directamente en esta clase.

Correr tests:
    python test_db.txt db_inicio.txt --nivel 1
"""

from __future__ import annotations
from dataclasses import dataclass, field
from bisect import bisect_right


@dataclass
class Entry:
    value: str
    expires_at: int | None = None

    def alive(self, ts) -> bool:
        return self.expires_at is None or self.expires_at > ts


class InMemoryDB:
    def __init__(self) -> None:
        self._data: dict[str, dict[str, Entry]] = {}
        self._backups: list[dict[str, dict[str, tuple[str, int | None]]]] = []
        self._backups_times: list[int] = []
    
    def _exist_entry(self, ts, key, field) -> Entry | None:
        entry = self._data.get(key, {}).get(field)
        if entry is None or not entry.alive(ts):
            return None
        return entry

    def _add(self, key, field, value, expires_at = None) -> None:
        self._data.setdefault(key, {})[field] = Entry(value, expires_at)

    def _delete(self, ts, key, field) -> None:
        del self._data[key][field]
        if len(self._data[key]) == 0:
            del self._data[key]
    
    def _alive_entries(self, ts, key) -> list[tuple[str, Entry]]:
        return sorted(
            (f, e) for f, e in self._data.get(key, {}).items() if e.alive(ts)
        )

    # ---------------- Nivel 1 ----------------
    def set(self, timestamp: int, key: str, field: str, value: str) -> None:
        self._add(key, field, value)

    def get(self, timestamp: int, key: str, field: str) -> str | None:
        entry = self._exist_entry(timestamp, key, field)
        return entry.value if entry else None

    def delete(self, timestamp: int, key: str, field: str) -> bool:
        value = self.get(timestamp, key, field)
        if value is None:
            return False
        self._delete(timestamp, key, field)
        return True

    def compare_and_set(self, timestamp: int, key: str, field: str,
                        expected: str, new_value: str) -> bool:
        entry = self._exist_entry(timestamp, key, field)
        if entry is None or entry.value != expected:
            return False
        
        entry.value = new_value
        return True

    # ---------------- Nivel 2 ----------------
    def scan(self, timestamp, key) -> list[str]:
        return [f"{f}({e.value})" for f, e in self._alive_entries(timestamp, key)]

    def scan_by_prefix(self, timestamp, key, prefix) -> list[str]:
        return [f"{f}({e.value})" for f, e in self._alive_entries(timestamp, key) if f.startswith(prefix)]
    
    # ---------------- Nivel 3 ----------------
    def set_with_ttl(self, timestamp, key, field, value, ttl) -> None:
        self._add(key, field, value, timestamp + ttl)

    # ---------------- Nivel 4 ----------------
    def backup(self, timestamp) -> int:
        snapshot = {}
        for key, entries in self._data.items():
            alive = {
                f: (
                    e.value, 
                    None if e.expires_at is None else e.expires_at - timestamp
                ) for f, e in entries.items() if e.alive(timestamp)
            }
            if len(alive) > 0:
                snapshot[key] = alive
        self._backups.append(snapshot)
        self._backups_times.append(timestamp)
        return len(snapshot)

    def restore(self, timestamp, timestamp_to_restore) -> bool:
        if len(self._backups_times) <= 0:
            return False
        i = bisect_right(self._backups_times, timestamp_to_restore) - 1
        if i < 0:
            return False
        self._data = {
            key: {
                field: Entry(value, None if ttl is None else timestamp + ttl)
                for field, (value, ttl) in entries.items()
            }
            for key, entries in self._backups[i].items()
        }
        return True