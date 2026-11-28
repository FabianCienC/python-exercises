"""
Tests por nivel para el ejercicio Sistema bancario.

Uso (funciona aunque los archivos sean .txt):
    python test_banco.txt banco_inicio-2.py              # todos los niveles
    python test_banco.txt banco_inicio-2.py --nivel 2    # solo hasta L2
    python test_banco.txt banco_inicio-2.py -v           # detalle de cada fallo

Cada test crea una instancia nueva de Bank.
"""

import argparse
import importlib.machinery
import importlib.util
import sys
import traceback

DAY = 86_400_000
TESTS = {1: [], 2: [], 3: [], 4: []}


def test(level):
    def deco(fn):
        TESTS[level].append(fn)
        return fn
    return deco


# ============================================================ NIVEL 1
@test(1)
def l1_create_account(b):
    assert b.create_account(1, "a") is True
    assert b.create_account(2, "a") is False

@test(1)
def l1_deposit(b):
    b.create_account(1, "a")
    assert b.deposit(2, "a", 100) == 100
    assert b.deposit(3, "a", 50) == 150

@test(1)
def l1_deposit_missing(b):
    assert b.deposit(1, "ghost", 10) is None

@test(1)
def l1_transfer_basic(b):
    b.create_account(1, "a"); b.create_account(2, "b")
    b.deposit(3, "a", 100)
    assert b.transfer(4, "a", "b", 30) == 70
    assert b.deposit(5, "b", 1) == 31, "el destino debe recibir el monto"

@test(1)
def l1_transfer_insufficient(b):
    b.create_account(1, "a"); b.create_account(2, "b")
    b.deposit(3, "a", 10)
    assert b.transfer(4, "a", "b", 11) is None
    assert b.deposit(5, "a", 0) == 10, "un transfer fallido no cambia saldos"
    assert b.deposit(6, "b", 0) == 0

@test(1)
def l1_transfer_invalid_accounts(b):
    b.create_account(1, "a")
    b.deposit(2, "a", 10)
    assert b.transfer(3, "a", "a", 5) is None, "misma cuenta"
    assert b.transfer(4, "a", "ghost", 5) is None
    assert b.transfer(5, "ghost", "a", 5) is None
    assert b.deposit(6, "a", 0) == 10

@test(1)
def l1_transfer_exact_balance(b):
    b.create_account(1, "a"); b.create_account(2, "b")
    b.deposit(3, "a", 40)
    assert b.transfer(4, "a", "b", 40) == 0


# ============================================================ NIVEL 2
@test(2)
def l2_order_by_outgoing(b):
    for i, acc in enumerate(["a", "b", "c"]):
        b.create_account(i + 1, acc)
    b.deposit(10, "a", 100); b.deposit(11, "b", 100)
    b.transfer(12, "a", "c", 10)
    b.transfer(13, "b", "c", 50)
    assert b.top_spenders(14, 3) == ["b(50)", "a(10)", "c(0)"]

@test(2)
def l2_ties_by_id(b):
    for i, acc in enumerate(["z", "m", "a"]):
        b.create_account(i + 1, acc)
    assert b.top_spenders(10, 2) == ["a(0)", "m(0)"]

@test(2)
def l2_n_bigger_than_count(b):
    b.create_account(1, "a")
    assert b.top_spenders(2, 5) == ["a(0)"]

@test(2)
def l2_deposits_dont_count(b):
    b.create_account(1, "a"); b.create_account(2, "b")
    b.deposit(3, "a", 1000)
    b.deposit(4, "b", 10)
    b.transfer(5, "b", "a", 5)
    assert b.top_spenders(6, 2) == ["b(5)", "a(0)"]

@test(2)
def l2_failed_transfer_doesnt_count(b):
    b.create_account(1, "a"); b.create_account(2, "b")
    b.transfer(3, "a", "b", 10)
    assert b.top_spenders(4, 2) == ["a(0)", "b(0)"]

@test(2)
def l2_outgoing_accumulates(b):
    b.create_account(1, "a"); b.create_account(2, "b")
    b.deposit(3, "a", 100)
    b.transfer(4, "a", "b", 10); b.transfer(5, "a", "b", 15)
    b.transfer(6, "b", "a", 25)
    assert b.top_spenders(7, 2) == ["a(25)", "b(25)"]


# ============================================================ NIVEL 3
@test(3)
def l3_payment_ids_global(b):
    b.create_account(1, "a"); b.create_account(2, "b")
    b.deposit(3, "a", 100); b.deposit(4, "b", 100)
    assert b.pay(5, "a", 10) == "payment1"
    assert b.pay(6, "b", 10) == "payment2"
    assert b.pay(7, "a", 10) == "payment3"

@test(3)
def l3_pay_invalid(b):
    b.create_account(1, "a")
    b.deposit(2, "a", 5)
    assert b.pay(3, "a", 6) is None
    assert b.pay(4, "ghost", 1) is None
    assert b.pay(5, "a", 5) == "payment1", "los pagos fallidos no consumen id"

@test(3)
def l3_pay_balance_and_outgoing(b):
    b.create_account(1, "a"); b.create_account(2, "b")
    b.deposit(3, "a", 100)
    b.pay(4, "a", 30)
    assert b.deposit(5, "a", 0) == 70
    assert b.top_spenders(6, 2) == ["a(30)", "b(0)"]

@test(3)
def l3_cashback_timing(b):
    b.create_account(1, "a")
    b.deposit(2, "a", 1000)
    b.pay(10, "a", 500)                       # cashback = 10
    assert b.deposit(10 + DAY - 1, "a", 0) == 500, "aún no llega"
    assert b.deposit(10 + DAY, "a", 0) == 510, "llega exactamente en ts + 24h"

@test(3)
def l3_cashback_floor(b):
    b.create_account(1, "a")
    b.deposit(2, "a", 1000)
    b.pay(3, "a", 149)                        # 149 * 2 / 100 = 2.98 -> 2
    assert b.deposit(3 + DAY, "a", 0) == 1000 - 149 + 2

@test(3)
def l3_payment_status(b):
    b.create_account(1, "a"); b.create_account(2, "b")
    b.deposit(2, "a", 100)
    p = b.pay(3, "a", 50)
    assert b.get_payment_status(4, "a", p) == "IN_PROGRESS"
    assert b.get_payment_status(5, "b", p) is None, "el pago no es de b"
    assert b.get_payment_status(6, "a", "payment99") is None
    assert b.get_payment_status(7, "ghost", p) is None
    assert b.get_payment_status(3 + DAY, "a", p) == "CASHBACK_RECEIVED"

@test(3)
def l3_cashback_doesnt_reduce_outgoing(b):
    b.create_account(1, "a")
    b.deposit(2, "a", 1000)
    b.pay(3, "a", 100)
    assert b.top_spenders(3 + DAY, 1) == ["a(100)"]

@test(3)
def l3_cashback_before_operation_same_ts(b):
    b.create_account(1, "a"); b.create_account(2, "b")
    b.deposit(2, "a", 100)
    b.pay(3, "a", 100)                        # saldo 0, cashback 2
    assert b.transfer(3 + DAY, "a", "b", 2) == 0, "el cashback se procesa antes de la operación"


# ============================================================ NIVEL 4
@test(4)
def l4_merge_basic(b):
    b.create_account(1, "a"); b.create_account(2, "b")
    b.deposit(3, "a", 10); b.deposit(4, "b", 20)
    assert b.merge_accounts(5, "a", "b") is True
    assert b.deposit(6, "a", 0) == 30
    assert b.deposit(7, "b", 1) is None, "la cuenta origen ya no existe"

@test(4)
def l4_merge_invalid(b):
    b.create_account(1, "a")
    b.deposit(2, "a", 10)
    assert b.merge_accounts(3, "a", "a") is False
    assert b.merge_accounts(4, "a", "ghost") is False
    assert b.merge_accounts(5, "ghost", "a") is False
    assert b.deposit(6, "a", 0) == 10

@test(4)
def l4_merge_outgoing(b):
    for i, acc in enumerate(["a", "b", "c"]):
        b.create_account(i + 1, acc)
    b.deposit(10, "a", 100); b.deposit(11, "b", 100)
    b.transfer(12, "a", "c", 10); b.transfer(13, "b", "c", 20)
    b.merge_accounts(14, "a", "b")
    assert b.top_spenders(15, 5) == ["a(30)", "c(0)"]

@test(4)
def l4_merge_moves_pending_cashback(b):
    b.create_account(1, "a"); b.create_account(2, "b")
    b.deposit(3, "b", 1000)
    p = b.pay(4, "b", 500)                    # cashback 10, pendiente
    b.merge_accounts(5, "a", "b")
    assert b.get_payment_status(6, "a", p) == "IN_PROGRESS"
    assert b.deposit(4 + DAY, "a", 0) == 510
    assert b.get_payment_status(4 + DAY + 1, "a", p) == "CASHBACK_RECEIVED"

@test(4)
def l4_recreated_source_is_fresh(b):
    b.create_account(1, "a"); b.create_account(2, "b")
    b.deposit(3, "b", 100)
    p = b.pay(4, "b", 10)
    b.merge_accounts(5, "a", "b")
    assert b.create_account(6, "b") is True
    assert b.deposit(7, "b", 0) == 0
    assert b.get_payment_status(8, "b", p) is None, "el pago ahora es de a"
    assert b.get_balance(9, "b", 4) is None, "la nueva b no existía en t=4"

@test(4)
def l4_get_balance_history(b):
    b.create_account(1, "a"); b.create_account(2, "b")
    b.deposit(5, "a", 100)
    b.transfer(10, "a", "b", 40)
    assert b.get_balance(20, "a", 0) is None, "antes de crearse"
    assert b.get_balance(20, "a", 1) == 0
    assert b.get_balance(20, "a", 7) == 100
    assert b.get_balance(20, "a", 10) == 60, "incluye las operaciones de ese timestamp"
    assert b.get_balance(20, "b", 15) == 40
    assert b.get_balance(20, "ghost", 15) is None

@test(4)
def l4_get_balance_includes_cashback_at_due(b):
    b.create_account(1, "a")
    b.deposit(2, "a", 1000)
    b.pay(10, "a", 500)
    q = 10 + 2 * DAY
    assert b.get_balance(q, "a", 10 + DAY - 1) == 500
    assert b.get_balance(q, "a", 10 + DAY) == 510

@test(4)
def l4_get_balance_after_merge(b):
    b.create_account(1, "a"); b.create_account(2, "b")
    b.deposit(3, "a", 10); b.deposit(4, "b", 20)
    b.merge_accounts(5, "a", "b")
    assert b.get_balance(6, "a", 4) == 10, "antes del merge, solo el saldo propio de a"
    assert b.get_balance(6, "a", 5) == 30
    assert b.get_balance(6, "b", 4) is None, "b ya no existe"

@test(4)
def l4_history_many_ops(b):
    b.create_account(1, "a")
    for t in range(2, 52):
        b.deposit(t, "a", 1)
    assert b.get_balance(100, "a", 26) == 25
    assert b.get_balance(100, "a", 1000) == 50


# ============================================================ RUNNER
def load_module(path):
    loader = importlib.machinery.SourceFileLoader("candidate", path)
    spec = importlib.util.spec_from_loader("candidate", loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules["candidate"] = module   # necesario para dataclasses
    loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="banco_inicio-2.py")
    parser.add_argument("--nivel", type=int, default=4)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    module = load_module(args.path)
    total_ok = total = 0
    for level in range(1, args.nivel + 1):
        ok = 0
        failures = []
        for fn in TESTS[level]:
            try:
                fn(module.Bank())
                ok += 1
            except Exception as exc:
                failures.append((fn.__name__, exc, traceback.format_exc()))
        total_ok += ok
        total += len(TESTS[level])
        mark = "OK " if ok == len(TESTS[level]) else "-- "
        print(f"{mark}Nivel {level}: {ok}/{len(TESTS[level])}")
        for name, exc, tb in failures:
            msg = str(exc) or type(exc).__name__
            print(f"     x {name}: {msg}")
            if args.verbose:
                print("       " + tb.replace("\n", "\n       "))
    print(f"\nTotal: {total_ok}/{total}")


if __name__ == "__main__":
    main()
