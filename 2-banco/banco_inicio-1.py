"""
Tu código va aquí. Empieza solo con el Nivel 1.
Cuando pases el nivel, agrega los métodos del siguiente directamente en esta clase.

Correr tests:
    python test_banco.txt banco_inicio.txt --nivel 1
"""

from __future__ import annotations
from dataclasses import dataclass, field
from bisect import bisect, bisect_right


@dataclass
class Account:
    account_id: str
    timestamp: int
    balance: int = 0
    outgoing: int = 0
    payments: set[str] = field(default_factory=set)
    history: list[tuple[int, int]] = field(default_factory=list)

@dataclass
class Payment:
    payment_id:str
    timestamp: int
    amount: int
    account_id: str
    status: str = "IN_PROGRESS"


class Bank:
    def __init__(self) -> None:
        self._accounts: dict[str, Account] = {}
        self._payments: dict[str, Payment] = {}
        self._payment_counter: int = 0

    def _create_account(self, timestamp: int, account_id: str) -> None:
        self._accounts[account_id] = Account(account_id, timestamp, history=[(timestamp, 0)])

    def _change_balance(self, timestamp: int, account_id: str, delta: int) -> None:
        acc = self._accounts[account_id]
        acc.balance += delta
        acc.history.append((timestamp, acc.balance))

    def _check_valid_cashback(self, timestamp: int, payment: Payment) -> bool:
        return timestamp >= payment.timestamp + 86_400_000

    def _apply_cashback(self, timestamp):
        valid_payments = [
            payment for payment in self._payments.values() 
            if self._check_valid_cashback(timestamp, payment) and payment.status == "IN_PROGRESS"
        ]
        for p in valid_payments:
            cashback = (p.amount * 2) // 100
            self._change_balance(p.timestamp + 86_400_000, p.account_id, cashback) 
            p.status = "CASHBACK_RECEIVED"

    # ---------------- Nivel 1 ----------------
    def create_account(self, timestamp: int, account_id: str) -> bool:
        self._apply_cashback(timestamp)
        if account_id in self._accounts:
            return False
        self._create_account(timestamp, account_id)
        return True
        
    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self._apply_cashback(timestamp)
        account = self._accounts.get(account_id)
        if account is None:
            return None
        self._change_balance(timestamp, account_id, amount)
        return account.balance

    def transfer(self, timestamp: int, source_id: str, target_id: str, amount: int) -> int | None:
        self._apply_cashback(timestamp)
        source = self._accounts.get(source_id)
        target = self._accounts.get(target_id)
        if source is None or target is None or target_id == source_id or source.balance < amount:
            return None
        self._change_balance(timestamp, source_id, -amount)
        source.outgoing += amount
        self._change_balance(timestamp, target_id, amount)
        return source.balance

    # ---------------- Nivel 2 ----------------
    def top_spenders(self, timestamp, n) -> list[str]:
        self._apply_cashback(timestamp)
        res_accounts = sorted(self._accounts.values(), key=lambda a: (-a.outgoing, a.account_id))
        if n <= len(self._accounts):
            res_accounts = res_accounts[:n]
        return [f"{acc.account_id}({acc.outgoing})" for acc in res_accounts]

    # ---------------- Nivel 3 ----------------
    def pay(self, timestamp, account_id, amount) -> str | None:
        self._apply_cashback(timestamp)

        account = self._accounts.get(account_id)
        if account is None:
            return None
        if account.balance < amount:
            return None

        self._change_balance(timestamp, account_id, -amount)
        account.outgoing += amount
        self._payment_counter += 1

        payment_id = f"payment{self._payment_counter}"
        self._payments[payment_id] = Payment(payment_id, timestamp, amount, account_id)
        account.payments.add(payment_id)

        return payment_id

    def get_payment_status(self, timestamp, account_id, payment_id) -> str | None:
        self._apply_cashback(timestamp)

        account = self._accounts.get(account_id)
        payment = self._payments.get(payment_id)
        if account is None or payment is None or payment.account_id != account_id:
            return None
        
        return payment.status

    # ---------------- Nivel 4 ----------------
    def merge_accounts(self, timestamp, target_id, source_id) -> bool:
        self._apply_cashback(timestamp)
        source = self._accounts.get(source_id)
        target = self._accounts.get(target_id)
        if source is None or target is None or target_id == source_id:
            return False

        self._change_balance(timestamp, target_id, source.balance)
        target.outgoing += source.outgoing

        for payment_id in source.payments:
            self._payments[payment_id].account_id = target_id
        target.payments.update(source.payments)

        del self._accounts[source_id]
        
        return True

    def get_balance(self, timestamp, account_id, time_at) -> int | None:
        self._apply_cashback(timestamp)
        account = self._accounts.get(account_id)
        if account is None:
            return None
        i = bisect_right(account.history, (time_at, float("inf"))) - 1
        return account.history[i][1] if i >= 0 else None
        