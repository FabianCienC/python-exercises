"""
Tu código va aquí. Empieza solo con el Nivel 1.
Cuando pases el nivel, agrega los métodos del siguiente directamente en esta clase.

Correr tests:
    python test_workers.txt workers_inicio.txt --nivel 1
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Session:
    start: int
    end: int
    compensation: int

@dataclass
class Promotion:
    position: str
    compensation: int
    start: int

@dataclass
class Worker:
    worker_id: str
    position: str
    compensation: int
    sessions: list[Session] = field(default_factory=list)
    entered_at: int = None
    total_time: int = 0
    pending: Promotion | None = None
    time_at_position: int = 0

INVALID = "invalid_request"

class WorkerSystem:
    def __init__(self) -> None:
        self._workers: dict[str, Worker] = {}
        self._double: list[tuple[int, int]] = []

    # ---------------- Nivel 1 ----------------
    def add_worker(self, worker_id: str, position: str, compensation: int) -> bool:
        if worker_id in self._workers:
            return False
        self._workers[worker_id] = Worker(worker_id, position, compensation)
        return True

    def register(self, worker_id: str, timestamp: int) -> str:
        w = self._workers.get(worker_id)
        if w is None:
            return INVALID

        if w.entered_at is None:
            if w.pending and w.pending.start <= timestamp:
                w.position = w.pending.position
                w.compensation = w.pending.compensation
                w.time_at_position = 0
                w.pending = None
            w.entered_at = timestamp

        else:
            duration = timestamp - w.entered_at
            w.sessions.append(Session(w.entered_at, timestamp, w.compensation))
            w.total_time += duration
            w.time_at_position += duration
            w.entered_at = None
        return "registered"
        
    def get(self, worker_id: str) -> int | None:
        if worker_id not in self._workers:
            return None
        w = self._workers[worker_id]
        times = [s.end - s.start for s in w.sessions]
        return sum(times)

    # ---------------- Nivel 2 ----------------
    def top_n_workers(self, n, position) -> list[str]:
        if n <= 0:
            return []
        candidates = [w for w in self._workers.values() if w.position == position]
        n = min(len(candidates), n)
        ranked = sorted(candidates, key=lambda w: (-w.time_at_position, w.worker_id))[:n]
        return [f"{w.worker_id}({w.time_at_position})" for w in ranked]

    # ---------------- Nivel 3 ----------------
    def promote(self, worker_id, new_position, new_compensation, start_timestamp) -> str:
        w = self._workers.get(worker_id)
        if w is None or w.pending is not None:
            return INVALID
        w.pending = Promotion(new_position, new_compensation, start_timestamp)
        return "success"

    def calc_salary(self, worker_id, start_timestamp, end_timestamp) -> int | None:
        w = self._workers.get(worker_id)
        if w is None or len(w.sessions) == 0:
            return None
        total = 0
        merged = self._merged_double()
        for s in w.sessions:
            a, b = max(s.start, start_timestamp), min(s.end, end_timestamp)
            if a >= b:
                continue
            normal = b - a
            double = sum(overlap(a, b, x, y) for x, y in merged)
            total += (normal + double) * s.compensation
        return total

    # ---------------- Nivel 4 ----------------
    def set_double_paid(self, start_timestamp, end_timestamp) -> None:
        self._double.append((start_timestamp, end_timestamp))

    def _merged_double(self) -> list[tuple[int, int]]:
        merged: list[list[int]] = []
        for start, end in sorted(self._double):
            if merged and merged[-1][1] > start:
                merged[-1][1] = max(merged[-1][1], end)
            else:
                merged.append([start, end])
        return [(start, end) for start, end in merged]

def overlap(a: int, b: int, x: int, y: int) -> int:
    return max(0, min(b, y) - max(a, x))