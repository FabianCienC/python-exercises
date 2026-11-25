"""
SOLUCIÓN DE REFERENCIA — Sistema bancario (L1–L4)

No abras este archivo hasta haber intentado el nivel correspondiente.
Correr tests contra esta solución (desde la carpeta principal):
    python test_banco.txt soluciones/solucion_banco.txt

Ideas clave (detalle en SOLUCION.md):
  1. Toda modificación de saldo pasa por _change_balance, que además registra el historial.
     Así get_balance (L4) sale "gratis" aunque llegue al final.
  2. Los cashbacks pendientes viven en un heap ordenado por (vencimiento, orden de creación)
     y se procesan al INICIO de cada método público.
  3. El pago guarda a qué cuenta pertenece; el cashback se acredita a esa cuenta al vencer.
     Si hubo un merge, basta con reasignar ese campo.
"""

from __future__ import annotations

import bisect
import heapq
from dataclasses import dataclass, field
from itertools import count

CASHBACK_DELAY = 86_400_000      # 24 h en milisegundos
CASHBACK_PERCENT = 2


@dataclass
class Account:
    account_id: str
    balance: int = 0
    outgoing: int = 0
    payments: set[str] = field(default_factory=set)
    # Historial en listas paralelas: history_ts[i] <-> history_bal[i]
    history_ts: list[int] = field(default_factory=list)
    history_bal: list[int] = field(default_factory=list)

    def record(self, ts: int) -> None:
        """Guarda el saldo actual en el tiempo ts (un solo registro por timestamp)."""
        if self.history_ts and self.history_ts[-1] == ts:
            self.history_bal[-1] = self.balance
        else:
            self.history_ts.append(ts)
            self.history_bal.append(self.balance)

    def balance_at(self, ts: int) -> int | None:
        i = bisect.bisect_right(self.history_ts, ts) - 1
        return self.history_bal[i] if i >= 0 else None


@dataclass
class Payment:
    payment_id: str
    account_id: str
    cashback: int
    due: int
    received: bool = False


class Bank:
    def __init__(self) -> None:
        self._accounts: dict[str, Account] = {}
        self._payments: dict[str, Payment] = {}
        self._pending: list[tuple[int, int, str]] = []   # heap: (due, n, payment_id)
        self._payment_numbers = count(1)

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------
    def _change_balance(self, account: Account, delta: int, ts: int) -> None:
        """Único lugar que modifica saldos: mantiene el historial sincronizado."""
        account.balance += delta
        account.record(ts)

    def _process_due(self, ts: int) -> None:
        """Acredita todos los cashbacks con vencimiento <= ts, en orden."""
        while self._pending and self._pending[0][0] <= ts:
            due, _, payment_id = heapq.heappop(self._pending)
            payment = self._payments[payment_id]
            # Se registra en su tiempo de vencimiento, no en ts: el historial queda exacto.
            self._change_balance(self._accounts[payment.account_id], payment.cashback, due)
            payment.received = True

    # ------------------------------------------------------------------
    # Nivel 1
    # ------------------------------------------------------------------
    def create_account(self, timestamp: int, account_id: str) -> bool:
        self._process_due(timestamp)
        if account_id in self._accounts:
            return False
        account = Account(account_id)
        account.record(timestamp)
        self._accounts[account_id] = account
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self._process_due(timestamp)
        account = self._accounts.get(account_id)
        if account is None:
            return None
        self._change_balance(account, amount, timestamp)
        return account.balance

    def transfer(self, timestamp: int, source_id: str, target_id: str, amount: int) -> int | None:
        self._process_due(timestamp)
        if source_id == target_id:
            return None
        source = self._accounts.get(source_id)
        target = self._accounts.get(target_id)
        if source is None or target is None or source.balance < amount:
            return None
        self._change_balance(source, -amount, timestamp)
        self._change_balance(target, amount, timestamp)
        source.outgoing += amount
        return source.balance

    # ------------------------------------------------------------------
    # Nivel 2
    # ------------------------------------------------------------------
    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        self._process_due(timestamp)
        if n <= 0:
            return []
        ranked = sorted(self._accounts.values(), key=lambda a: (-a.outgoing, a.account_id))[:n]
        return [f"{a.account_id}({a.outgoing})" for a in ranked]

    # ------------------------------------------------------------------
    # Nivel 3
    # ------------------------------------------------------------------
    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        self._process_due(timestamp)
        account = self._accounts.get(account_id)
        if account is None or account.balance < amount:
            return None
        self._change_balance(account, -amount, timestamp)
        account.outgoing += amount

        number = next(self._payment_numbers)           # solo pagos exitosos consumen id
        payment_id = f"payment{number}"
        due = timestamp + CASHBACK_DELAY
        self._payments[payment_id] = Payment(
            payment_id, account_id, amount * CASHBACK_PERCENT // 100, due
        )
        account.payments.add(payment_id)
        heapq.heappush(self._pending, (due, number, payment_id))
        return payment_id

    def get_payment_status(self, timestamp: int, account_id: str, payment_id: str) -> str | None:
        self._process_due(timestamp)
        if account_id not in self._accounts:
            return None
        payment = self._payments.get(payment_id)
        if payment is None or payment.account_id != account_id:
            return None
        return "CASHBACK_RECEIVED" if payment.received else "IN_PROGRESS"

    # ------------------------------------------------------------------
    # Nivel 4
    # ------------------------------------------------------------------
    def merge_accounts(self, timestamp: int, target_id: str, source_id: str) -> bool:
        self._process_due(timestamp)
        if target_id == source_id:
            return False
        target = self._accounts.get(target_id)
        source = self._accounts.get(source_id)
        if target is None or source is None:
            return False

        # Los pagos (y sus cashbacks pendientes) pasan a la cuenta destino.
        for payment_id in source.payments:
            self._payments[payment_id].account_id = target_id
        target.payments |= source.payments
        target.outgoing += source.outgoing
        self._change_balance(target, source.balance, timestamp)

        del self._accounts[source_id]
        return True

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        self._process_due(timestamp)
        account = self._accounts.get(account_id)
        if account is None:
            return None
        return account.balance_at(time_at)
