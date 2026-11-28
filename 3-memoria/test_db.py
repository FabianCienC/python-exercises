"""
Tests por nivel para el ejercicio Base de datos en memoria.

Uso (funciona aunque los archivos sean .txt):
    python test_db.txt db_inicio-2.py              # todos los niveles
    python test_db.txt db_inicio-2.py --nivel 2    # solo hasta L2
    python test_db.txt db_inicio-2.py -v           # detalle de cada fallo

Cada test crea una instancia nueva de InMemoryDB.
"""

import argparse
import importlib.machinery
import importlib.util
import sys
import traceback

TESTS = {1: [], 2: [], 3: [], 4: []}


def test(level):
    def deco(fn):
        TESTS[level].append(fn)
        return fn
    return deco


# ============================================================ NIVEL 1
@test(1)
def l1_set_get(db):
    db.set(1, "user1", "name", "Ana")
    assert db.get(2, "user1", "name") == "Ana"

@test(1)
def l1_get_missing(db):
    db.set(1, "user1", "name", "Ana")
    assert db.get(2, "user1", "age") is None
    assert db.get(3, "user2", "name") is None

@test(1)
def l1_overwrite(db):
    db.set(1, "k", "f", "a")
    db.set(2, "k", "f", "b")
    assert db.get(3, "k", "f") == "b"

@test(1)
def l1_delete(db):
    db.set(1, "k", "f", "a")
    db.set(2, "k", "g", "b")
    assert db.delete(3, "k", "f") is True
    assert db.get(4, "k", "f") is None
    assert db.get(5, "k", "g") == "b", "borrar un campo no afecta a los demás"

@test(1)
def l1_delete_missing(db):
    assert db.delete(1, "k", "f") is False
    db.set(2, "k", "f", "a")
    assert db.delete(3, "k", "x") is False

@test(1)
def l1_delete_then_set_again(db):
    db.set(1, "k", "f", "a")
    db.delete(2, "k", "f")
    db.set(3, "k", "f", "z")
    assert db.get(4, "k", "f") == "z"

@test(1)
def l1_compare_and_set(db):
    db.set(1, "k", "f", "a")
    assert db.compare_and_set(2, "k", "f", "x", "b") is False
    assert db.get(3, "k", "f") == "a"
    assert db.compare_and_set(4, "k", "f", "a", "b") is True
    assert db.get(5, "k", "f") == "b"
    assert db.compare_and_set(6, "k", "nope", "a", "b") is False
    assert db.get(7, "k", "nope") is None, "un CAS fallido no crea el campo"


# ============================================================ NIVEL 2
@test(2)
def l2_scan_sorted(db):
    db.set(1, "k", "c", "3"); db.set(2, "k", "a", "1"); db.set(3, "k", "b", "2")
    assert db.scan(4, "k") == ["a(1)", "b(2)", "c(3)"]

@test(2)
def l2_scan_missing_key(db):
    assert db.scan(1, "ghost") == []

@test(2)
def l2_scan_by_prefix(db):
    db.set(1, "k", "addr_city", "CUU"); db.set(2, "k", "addr_zip", "31000")
    db.set(3, "k", "name", "Fab")
    assert db.scan_by_prefix(4, "k", "addr_") == ["addr_city(CUU)", "addr_zip(31000)"]

@test(2)
def l2_prefix_no_match(db):
    db.set(1, "k", "a", "1")
    assert db.scan_by_prefix(2, "k", "z") == []
    assert db.scan_by_prefix(3, "ghost", "a") == []

@test(2)
def l2_deleted_excluded(db):
    db.set(1, "k", "a", "1"); db.set(2, "k", "b", "2")
    db.delete(3, "k", "a")
    assert db.scan(4, "k") == ["b(2)"]

@test(2)
def l2_empty_prefix_and_isolation(db):
    db.set(1, "k1", "a", "1"); db.set(2, "k2", "a", "X")
    assert db.scan_by_prefix(3, "k1", "") == ["a(1)"], "solo campos de esa llave"


# ============================================================ NIVEL 3
@test(3)
def l3_ttl_alive_then_expired(db):
    db.set_with_ttl(10, "k", "f", "v", 5)     # vive en [10, 15)
    assert db.get(14, "k", "f") == "v"
    assert db.get(15, "k", "f") is None, "expira exactamente en ts + ttl"

@test(3)
def l3_set_clears_ttl(db):
    db.set_with_ttl(10, "k", "f", "v", 5)
    db.set(12, "k", "f", "w")
    assert db.get(100, "k", "f") == "w", "set normal no expira"

@test(3)
def l3_ttl_overwrite(db):
    db.set_with_ttl(10, "k", "f", "v", 5)
    db.set_with_ttl(12, "k", "f", "v2", 10)   # ahora vive hasta 22
    assert db.get(20, "k", "f") == "v2"
    assert db.get(22, "k", "f") is None

@test(3)
def l3_scan_excludes_expired(db):
    db.set(1, "k", "a", "1")
    db.set_with_ttl(1, "k", "b", "2", 5)
    assert db.scan(5, "k") == ["a(1)", "b(2)"]
    assert db.scan(6, "k") == ["a(1)"]
    assert db.scan_by_prefix(6, "k", "b") == []

@test(3)
def l3_delete_expired(db):
    db.set_with_ttl(1, "k", "f", "v", 5)
    assert db.delete(6, "k", "f") is False

@test(3)
def l3_cas_on_expired(db):
    db.set_with_ttl(1, "k", "f", "v", 5)
    assert db.compare_and_set(6, "k", "f", "v", "w") is False
    assert db.get(7, "k", "f") is None

@test(3)
def l3_cas_keeps_ttl(db):
    db.set_with_ttl(1, "k", "f", "v", 10)     # expira en 11
    assert db.compare_and_set(5, "k", "f", "v", "w") is True
    assert db.get(10, "k", "f") == "w"
    assert db.get(11, "k", "f") is None, "CAS conserva la expiración original"

@test(3)
def l3_set_after_expired(db):
    db.set_with_ttl(1, "k", "f", "v", 2)
    db.set(5, "k", "f", "nuevo")
    assert db.get(6, "k", "f") == "nuevo"


# ============================================================ NIVEL 4
@test(4)
def l4_backup_counts_keys(db):
    db.set(1, "a", "f", "1"); db.set(2, "a", "g", "2"); db.set(3, "b", "f", "3")
    assert db.backup(4) == 2

@test(4)
def l4_backup_excludes_expired(db):
    db.set(1, "a", "f", "1")
    db.set_with_ttl(1, "b", "f", "2", 3)      # expira en 4
    assert db.backup(4) == 1
    assert db.backup(5) == 1

@test(4)
def l4_restore_replaces_state(db):
    db.set(1, "a", "f", "1")
    db.backup(2)
    db.set(3, "a", "f", "CHANGED")
    db.set(4, "b", "x", "new")
    assert db.restore(5, 2) is True
    assert db.get(6, "a", "f") == "1"
    assert db.get(7, "b", "x") is None, "lo creado después del backup desaparece"

@test(4)
def l4_restore_no_backup(db):
    db.set(1, "a", "f", "1")
    db.backup(10)
    assert db.restore(20, 5) is False, "no hay backup en t <= 5"
    assert db.get(21, "a", "f") == "1", "un restore fallido no cambia nada"

@test(4)
def l4_restore_picks_latest_before(db):
    db.set(1, "a", "f", "v1"); db.backup(2)
    db.set(3, "a", "f", "v2"); db.backup(4)
    db.set(5, "a", "f", "v3"); db.backup(6)
    db.restore(10, 5)
    assert db.get(11, "a", "f") == "v2"
    db.restore(12, 6)
    assert db.get(13, "a", "f") == "v3"

@test(4)
def l4_restore_recomputes_ttl(db):
    db.set_with_ttl(10, "a", "f", "v", 20)    # expira en 30; restante en t=20 -> 10
    db.backup(20)
    db.restore(100, 20)                        # ahora vive hasta 110
    assert db.get(109, "a", "f") == "v"
    assert db.get(110, "a", "f") is None

@test(4)
def l4_restore_no_ttl_stays(db):
    db.set(1, "a", "f", "v")
    db.backup(2)
    db.restore(1000, 2)
    assert db.get(10**9, "a", "f") == "v"

@test(4)
def l4_backup_isolated(db):
    db.set(1, "a", "f", "v")
    db.backup(2)
    db.compare_and_set(3, "a", "f", "v", "mutado")
    db.delete(4, "a", "f")
    db.restore(5, 2)
    assert db.get(6, "a", "f") == "v", "el backup no comparte objetos con el estado vivo"
    db.compare_and_set(7, "a", "f", "v", "otra")
    db.restore(8, 2)
    assert db.get(9, "a", "f") == "v", "restaurar dos veces da lo mismo"

@test(4)
def l4_scan_after_restore(db):
    db.set(1, "a", "x", "1")
    db.set_with_ttl(1, "a", "y", "2", 10)     # restante en t=5 -> 6
    db.backup(5)
    db.restore(50, 5)
    assert db.scan(55, "a") == ["x(1)", "y(2)"]
    assert db.scan(56, "a") == ["x(1)"]


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
    parser.add_argument("path", nargs="?", default="db_inicio-2.py")
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
                fn(module.InMemoryDB())
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
