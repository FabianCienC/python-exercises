"""
Tests por nivel para el ejercicio Gestión de trabajadores.

Uso (funciona aunque los archivos sean .txt):
    python test_workers.txt workers_inicio-2.py              # todos los niveles
    python test_workers.txt workers_inicio-2.py --nivel 2    # solo hasta L2
    python test_workers.txt workers_inicio-2.py -v           # detalle de cada fallo

Cada test crea una instancia nueva de WorkerSystem.
"""

import argparse
import importlib.machinery
import importlib.util
import sys
import traceback

DEFAULT_PATH = "workers_inicio-2.py"
CLASS_NAME = "WorkerSystem"
TESTS = {1: [], 2: [], 3: [], 4: []}


def test(level):
    def deco(fn):
        TESTS[level].append(fn)
        return fn
    return deco


# ============================================================ NIVEL 1
@test(1)
def l1_add_worker(s):
    assert s.add_worker("ana", "Junior", 10) is True
    assert s.add_worker("ana", "Senior", 99) is False

@test(1)
def l1_register_missing(s):
    assert s.register("ghost", 1) == "invalid_request"

@test(1)
def l1_register_ok(s):
    s.add_worker("ana", "Junior", 10)
    assert s.register("ana", 10) == "registered"
    assert s.register("ana", 25) == "registered"

@test(1)
def l1_get_one_session(s):
    s.add_worker("ana", "Junior", 10)
    s.register("ana", 10); s.register("ana", 25)
    assert s.get("ana") == 15

@test(1)
def l1_open_session_not_counted(s):
    s.add_worker("ana", "Junior", 10)
    s.register("ana", 10); s.register("ana", 20)
    s.register("ana", 30)                 # entra y no ha salido
    assert s.get("ana") == 10

@test(1)
def l1_sessions_accumulate(s):
    s.add_worker("ana", "Junior", 10)
    s.add_worker("beto", "Junior", 10)
    s.register("ana", 1); s.register("beto", 2)
    s.register("ana", 5); s.register("beto", 12)
    s.register("ana", 20); s.register("ana", 23)
    assert s.get("ana") == 7
    assert s.get("beto") == 10

@test(1)
def l1_get_missing(s):
    assert s.get("ghost") is None
    s.add_worker("ana", "Junior", 10)
    assert s.get("ana") == 0


# ============================================================ NIVEL 2
def _work(s, wid, start, end):
    s.register(wid, start); s.register(wid, end)

@test(2)
def l2_top_by_time(s):
    for w in ["a", "b", "c"]:
        s.add_worker(w, "Junior", 10)
    _work(s, "a", 1, 6); _work(s, "b", 10, 30); _work(s, "c", 40, 50)
    assert s.top_n_workers(3, "Junior") == ["b(20)", "c(10)", "a(5)"]

@test(2)
def l2_ties_by_id(s):
    for w in ["zoe", "max", "ana"]:
        s.add_worker(w, "Junior", 10)
    assert s.top_n_workers(2, "Junior") == ["ana(0)", "max(0)"]

@test(2)
def l2_filter_by_position(s):
    s.add_worker("a", "Junior", 10); s.add_worker("b", "Senior", 20)
    _work(s, "a", 1, 5); _work(s, "b", 6, 100)
    assert s.top_n_workers(5, "Junior") == ["a(4)"]
    assert s.top_n_workers(5, "Senior") == ["b(94)"]

@test(2)
def l2_n_bigger(s):
    s.add_worker("a", "Junior", 10)
    assert s.top_n_workers(10, "Junior") == ["a(0)"]

@test(2)
def l2_no_one(s):
    s.add_worker("a", "Junior", 10)
    assert s.top_n_workers(3, "CEO") == []

@test(2)
def l2_open_session_excluded(s):
    s.add_worker("a", "Junior", 10); s.add_worker("b", "Junior", 10)
    _work(s, "a", 1, 3)
    s.register("b", 4)                     # b sigue dentro
    assert s.top_n_workers(2, "Junior") == ["a(2)", "b(0)"]


# ============================================================ NIVEL 3
@test(3)
def l3_promote_results(s):
    s.add_worker("a", "Junior", 10)
    assert s.promote("ghost", "Senior", 20, 100) == "invalid_request"
    assert s.promote("a", "Senior", 20, 100) == "success"
    assert s.promote("a", "Lead", 30, 200) == "invalid_request", "ya tiene un ascenso pendiente"

@test(3)
def l3_promotion_applies_on_entry_after_start(s):
    s.add_worker("a", "Junior", 10)
    s.promote("a", "Senior", 20, 100)
    _work(s, "a", 50, 60)                 # entra antes de 100: sigue Junior
    assert s.top_n_workers(5, "Junior") == ["a(10)"]
    _work(s, "a", 100, 110)               # entra en 100: ya es Senior
    assert s.top_n_workers(5, "Junior") == []
    assert s.top_n_workers(5, "Senior") == ["a(10)"], "tiempo en la posición actual"

@test(3)
def l3_session_in_progress_keeps_old(s):
    s.add_worker("a", "Junior", 10)
    s.register("a", 90)
    s.promote("a", "Senior", 20, 100)
    s.register("a", 120)                  # sale: la sesión era de Junior
    assert s.top_n_workers(5, "Junior") == ["a(30)"]
    assert s.calc_salary("a", 0, 1000) == 300

@test(3)
def l3_get_is_total(s):
    s.add_worker("a", "Junior", 10)
    _work(s, "a", 1, 11)
    s.promote("a", "Senior", 20, 50)
    _work(s, "a", 50, 55)
    assert s.get("a") == 15

@test(3)
def l3_salary_basic(s):
    s.add_worker("a", "Junior", 10)
    _work(s, "a", 10, 20)
    assert s.calc_salary("a", 0, 100) == 100

@test(3)
def l3_salary_partial_overlap(s):
    s.add_worker("a", "Junior", 10)
    _work(s, "a", 10, 20)
    _work(s, "a", 30, 40)
    assert s.calc_salary("a", 15, 35) == 100   # 5 de la 1ª + 5 de la 2ª
    assert s.calc_salary("a", 20, 30) == 0
    assert s.calc_salary("a", 12, 13) == 10

@test(3)
def l3_salary_uses_rate_per_session(s):
    s.add_worker("a", "Junior", 10)
    _work(s, "a", 0, 10)
    s.promote("a", "Senior", 50, 20)
    _work(s, "a", 20, 30)
    assert s.calc_salary("a", 0, 100) == 10 * 10 + 10 * 50

@test(3)
def l3_salary_missing(s):
    assert s.calc_salary("ghost", 0, 10) is None

@test(3)
def l3_second_promotion_after_first_applied(s):
    s.add_worker("a", "Junior", 10)
    s.promote("a", "Senior", 20, 10)
    _work(s, "a", 10, 15)
    assert s.promote("a", "Lead", 30, 20) == "success"
    _work(s, "a", 20, 22)
    assert s.top_n_workers(5, "Lead") == ["a(2)"]
    assert s.calc_salary("a", 0, 100) == 5 * 20 + 2 * 30


# ============================================================ NIVEL 4
@test(4)
def l4_double_full(s):
    s.add_worker("a", "Junior", 10)
    _work(s, "a", 10, 20)
    s.set_double_paid(0, 100)
    assert s.calc_salary("a", 0, 100) == 200

@test(4)
def l4_double_partial(s):
    s.add_worker("a", "Junior", 10)
    _work(s, "a", 10, 20)
    s.set_double_paid(15, 25)
    assert s.calc_salary("a", 0, 100) == 5 * 10 + 5 * 20

@test(4)
def l4_double_no_stacking(s):
    s.add_worker("a", "Junior", 10)
    _work(s, "a", 0, 10)
    s.set_double_paid(0, 8)
    s.set_double_paid(4, 10)              # se traslapan en [4, 8)
    assert s.calc_salary("a", 0, 10) == 200, "el doble pago no se acumula"

@test(4)
def l4_double_outside_query(s):
    s.add_worker("a", "Junior", 10)
    _work(s, "a", 0, 20)
    s.set_double_paid(0, 10)
    assert s.calc_salary("a", 10, 20) == 100

@test(4)
def l4_double_with_rate_change(s):
    s.add_worker("a", "Junior", 10)
    _work(s, "a", 0, 10)
    s.promote("a", "Senior", 30, 20)
    _work(s, "a", 20, 30)
    s.set_double_paid(5, 25)
    assert s.calc_salary("a", 0, 100) == (5 * 10 + 5 * 20) + (5 * 60 + 5 * 30)

@test(4)
def l4_multiple_disjoint(s):
    s.add_worker("a", "Junior", 1)
    _work(s, "a", 0, 100)
    s.set_double_paid(10, 20)
    s.set_double_paid(50, 60)
    s.set_double_paid(90, 200)
    assert s.calc_salary("a", 0, 100) == 100 + 10 + 10 + 10

@test(4)
def l4_retroactive(s):
    s.add_worker("a", "Junior", 10)
    _work(s, "a", 0, 10)
    assert s.calc_salary("a", 0, 10) == 100
    s.set_double_paid(0, 5)               # se define después: aplica igual
    assert s.calc_salary("a", 0, 10) == 150

@test(4)
def l4_touching_periods(s):
    s.add_worker("a", "Junior", 1)
    _work(s, "a", 0, 10)
    s.set_double_paid(0, 5)
    s.set_double_paid(5, 10)              # se tocan sin traslaparse
    assert s.calc_salary("a", 0, 10) == 20


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
    parser.add_argument("path", nargs="?", default=DEFAULT_PATH)
    parser.add_argument("--nivel", type=int, default=4)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    module = load_module(args.path)
    cls = getattr(module, CLASS_NAME)
    total_ok = total = 0
    for level in range(1, args.nivel + 1):
        ok = 0
        failures = []
        for fn in TESTS[level]:
            try:
                fn(cls())
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
