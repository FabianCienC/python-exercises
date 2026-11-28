"""
SOLUCIÓN DE REFERENCIA — Gestión de trabajadores (L1–L4)

No abras este archivo hasta haber intentado el nivel correspondiente.
Correr tests contra esta solución (desde la carpeta principal):
    python test_workers.txt soluciones/solucion_workers.txt

Ideas clave (detalle en SOLUCION.md):
  1. Guardar cada sesión cerrada como un objeto Session(start, end, compensation) desde el L1.
     El total de tiempo es una suma; el salario del L3 sale de esas mismas sesiones.
  2. La compensación se "congela" en la sesión: si después hay un ascenso, las sesiones
     viejas se siguen pagando con la tarifa que tenían.
  3. Un ascenso es un evento pendiente que se aplica al ENTRAR, cuando ts >= start.
  4. Intervalos semiabiertos [a, b): intersección = max(0, min(b1, b2) - max(a1, a2)).
     Para periodos dobles que se traslapan, primero se fusionan (merge intervals).
"""

from __future__ import annotations

from dataclasses import dataclass, field

INVALID = "invalid_request"


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
    entered_at: int | None = None          # None = fuera de la oficina
    total_time: int = 0
    position_time: int = 0                 # tiempo en la posición actual (L3)
    pending: Promotion | None = None


def overlap(a1: int, b1: int, a2: int, b2: int) -> int:
    """Longitud de la intersección de [a1, b1) y [a2, b2)."""
    return max(0, min(b1, b2) - max(a1, a2))


class WorkerSystem:
    def __init__(self) -> None:
        self._workers: dict[str, Worker] = {}
        self._double_periods: list[tuple[int, int]] = []

    # ------------------------------------------------------------------
    # Nivel 1
    # ------------------------------------------------------------------
    def add_worker(self, worker_id: str, position: str, compensation: int) -> bool:
        if worker_id in self._workers:
            return False
        self._workers[worker_id] = Worker(worker_id, position, compensation)
        return True

    def register(self, worker_id: str, timestamp: int) -> str:
        w = self._workers.get(worker_id)
        if w is None:
            return INVALID

        if w.entered_at is None:                      # entra
            if w.pending and w.pending.start <= timestamp:
                w.position = w.pending.position
                w.compensation = w.pending.compensation
                w.position_time = 0
                w.pending = None
            w.entered_at = timestamp
        else:                                         # sale: se cierra la sesión
            duration = timestamp - w.entered_at
            w.sessions.append(Session(w.entered_at, timestamp, w.compensation))
            w.total_time += duration
            w.position_time += duration
            w.entered_at = None
        return "registered"

    def get(self, worker_id: str) -> int | None:
        w = self._workers.get(worker_id)
        return w.total_time if w else None

    # ------------------------------------------------------------------
    # Nivel 2
    # ------------------------------------------------------------------
    def top_n_workers(self, n: int, position: str) -> list[str]:
        if n <= 0:
            return []
        candidates = [w for w in self._workers.values() if w.position == position]
        ranked = sorted(candidates, key=lambda w: (-w.position_time, w.worker_id))[:n]
        return [f"{w.worker_id}({w.position_time})" for w in ranked]

    # ------------------------------------------------------------------
    # Nivel 3
    # ------------------------------------------------------------------
    def promote(self, worker_id: str, new_position: str, new_compensation: int,
                start_timestamp: int) -> str:
        w = self._workers.get(worker_id)
        if w is None or w.pending is not None:
            return INVALID
        w.pending = Promotion(new_position, new_compensation, start_timestamp)
        return "success"

    def calc_salary(self, worker_id: str, start_timestamp: int, end_timestamp: int) -> int | None:
        w = self._workers.get(worker_id)
        if w is None:
            return None
        merged = self._merged_double_periods()
        total = 0
        for s in w.sessions:
            a, b = max(s.start, start_timestamp), min(s.end, end_timestamp)
            if a >= b:
                continue
            normal = b - a
            doubled = sum(overlap(a, b, ds, de) for ds, de in merged)
            total += (normal + doubled) * s.compensation   # tiempo doble se paga una vez extra
        return total

    # ------------------------------------------------------------------
    # Nivel 4
    # ------------------------------------------------------------------
    def set_double_paid(self, start_timestamp: int, end_timestamp: int) -> None:
        self._double_periods.append((start_timestamp, end_timestamp))

    def _merged_double_periods(self) -> list[tuple[int, int]]:
        """Fusiona periodos traslapados para que el doble pago no se acumule."""
        merged: list[list[int]] = []
        for start, end in sorted(self._double_periods):
            if merged and start <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], end)
            else:
                merged.append([start, end])
        return [(s, e) for s, e in merged]
