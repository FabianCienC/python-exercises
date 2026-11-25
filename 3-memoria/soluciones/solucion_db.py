"""
SOLUCIÓN DE REFERENCIA — Base de datos en memoria con TTL (L1–L4)

No abras este archivo hasta haber intentado el nivel correspondiente.
Correr tests contra esta solución (desde la carpeta principal):
    python test_db.txt soluciones/solucion_db.txt

Ideas clave (detalle en SOLUCION.md):
  1. Cada campo es un objeto Entry(value, expires_at); expires_at=None significa "no expira".
  2. Expiración LAZY: nada se borra en segundo plano; toda lectura pregunta entry.alive(ts).
     Un solo helper (_get_alive) concentra esa regla.
  3. Los backups guardan VALORES y TTL RESTANTE (no el expires_at absoluto),
     para recalcular la expiración relativa al momento del restore.
  4. Backups en listas paralelas ordenadas por tiempo -> bisect para "el último <= T".
"""

from __future__ import annotations

import bisect
from dataclasses import dataclass


@dataclass
class Entry:
    value: str
    expires_at: int | None = None     # None = no expira

    def alive(self, ts: int) -> bool:
        return self.expires_at is None or ts < self.expires_at


# Snapshot: key -> field -> (value, ttl_restante | None)
Snapshot = dict[str, dict[str, tuple[str, int | None]]]


class InMemoryDB:
    def __init__(self) -> None:
        self._data: dict[str, dict[str, Entry]] = {}
        self._backup_times: list[int] = []
        self._backups: list[Snapshot] = []

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------
    def _get_alive(self, ts: int, key: str, field: str) -> Entry | None:
        """Único lugar donde se decide si un campo 'existe' en el tiempo ts."""
        entry = self._data.get(key, {}).get(field)
        if entry is None or not entry.alive(ts):
            return None
        return entry

    def _alive_fields(self, ts: int, key: str) -> list[tuple[str, Entry]]:
        return sorted(
            (f, e) for f, e in self._data.get(key, {}).items() if e.alive(ts)
        )

    def _put(self, key: str, field: str, entry: Entry) -> None:
        self._data.setdefault(key, {})[field] = entry

    def _remove(self, key: str, field: str) -> None:
        fields = self._data[key]
        del fields[field]
        if not fields:                 # no dejar llaves vacías
            del self._data[key]

    # ------------------------------------------------------------------
    # Nivel 1
    # ------------------------------------------------------------------
    def set(self, timestamp: int, key: str, field: str, value: str) -> None:
        self._put(key, field, Entry(value))

    def get(self, timestamp: int, key: str, field: str) -> str | None:
        entry = self._get_alive(timestamp, key, field)
        return entry.value if entry else None

    def delete(self, timestamp: int, key: str, field: str) -> bool:
        if self._get_alive(timestamp, key, field) is None:
            return False
        self._remove(key, field)
        return True

    def compare_and_set(self, timestamp: int, key: str, field: str,
                        expected: str, new_value: str) -> bool:
        entry = self._get_alive(timestamp, key, field)
        if entry is None or entry.value != expected:
            return False
        entry.value = new_value        # L3: se conserva expires_at
        return True

    # ------------------------------------------------------------------
    # Nivel 2
    # ------------------------------------------------------------------
    def scan(self, timestamp: int, key: str) -> list[str]:
        return [f"{f}({e.value})" for f, e in self._alive_fields(timestamp, key)]

    def scan_by_prefix(self, timestamp: int, key: str, prefix: str) -> list[str]:
        return [f"{f}({e.value})" for f, e in self._alive_fields(timestamp, key)
                if f.startswith(prefix)]

    # ------------------------------------------------------------------
    # Nivel 3
    # ------------------------------------------------------------------
    def set_with_ttl(self, timestamp: int, key: str, field: str, value: str, ttl: int) -> None:
        self._put(key, field, Entry(value, timestamp + ttl))

    # ------------------------------------------------------------------
    # Nivel 4
    # ------------------------------------------------------------------
    def backup(self, timestamp: int) -> int:
        snapshot: Snapshot = {}
        for key, fields in self._data.items():
            alive = {
                f: (e.value, None if e.expires_at is None else e.expires_at - timestamp)
                for f, e in fields.items() if e.alive(timestamp)
            }
            if alive:
                snapshot[key] = alive
        # Timestamps crecientes: append mantiene las listas ordenadas.
        self._backup_times.append(timestamp)
        self._backups.append(snapshot)
        return len(snapshot)

    def restore(self, timestamp: int, timestamp_to_restore: int) -> bool:
        i = bisect.bisect_right(self._backup_times, timestamp_to_restore) - 1
        if i < 0:
            return False
        self._data = {
            key: {
                f: Entry(value, None if remaining is None else timestamp + remaining)
                for f, (value, remaining) in fields.items()
            }
            for key, fields in self._backups[i].items()
        }
        return True
