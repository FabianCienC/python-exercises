"""
Tests por nivel para el ejercicio In-Memory Cloud Storage.

Uso (funciona aunque los archivos sean .txt):
    python test_cloud_storage.txt cloud_storage_inicio-2.py          # todos los niveles
    python test_cloud_storage.txt cloud_storage_inicio-2.py --nivel 2 # solo hasta L2
    python test_cloud_storage.txt cloud_storage_inicio-2.py -v        # muestra el detalle de cada fallo

Cada test crea una instancia nueva de CloudStorage.
Un test que lanza una excepción (p. ej. método no implementado) cuenta como fallido.
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
def l1_add_and_get(cs):
    assert cs.add_file("a.txt", 10) is True
    assert cs.get_file_size("a.txt") == 10

@test(1)
def l1_duplicate_add_fails(cs):
    assert cs.add_file("a.txt", 10) is True
    assert cs.add_file("a.txt", 99) is False
    assert cs.get_file_size("a.txt") == 10, "el tamaño original no debe cambiar"

@test(1)
def l1_get_missing(cs):
    assert cs.get_file_size("nope") is None

@test(1)
def l1_delete_returns_size(cs):
    cs.add_file("a.txt", 7)
    assert cs.delete_file("a.txt") == 7
    assert cs.get_file_size("a.txt") is None

@test(1)
def l1_delete_missing(cs):
    assert cs.delete_file("nope") is None

@test(1)
def l1_readd_after_delete(cs):
    cs.add_file("a.txt", 7)
    cs.delete_file("a.txt")
    assert cs.add_file("a.txt", 3) is True
    assert cs.get_file_size("a.txt") == 3

@test(1)
def l1_many_files_independent(cs):
    for i in range(50):
        assert cs.add_file(f"f{i}", i) is True
    assert cs.delete_file("f10") == 10
    assert cs.get_file_size("f11") == 11
    assert cs.get_file_size("f10") is None


# ============================================================ NIVEL 2
@test(2)
def l2_order_by_size_desc(cs):
    cs.add_file("dir/a", 5); cs.add_file("dir/b", 20); cs.add_file("dir/c", 10)
    assert cs.get_n_largest("dir/", 3) == ["dir/b(20)", "dir/c(10)", "dir/a(5)"]

@test(2)
def l2_ties_by_name(cs):
    cs.add_file("x/c", 10); cs.add_file("x/a", 10); cs.add_file("x/b", 10)
    assert cs.get_n_largest("x/", 2) == ["x/a(10)", "x/b(10)"]

@test(2)
def l2_prefix_filter(cs):
    cs.add_file("img/1", 100); cs.add_file("doc/1", 500); cs.add_file("img/2", 50)
    assert cs.get_n_largest("img/", 5) == ["img/1(100)", "img/2(50)"]

@test(2)
def l2_n_bigger_than_count(cs):
    cs.add_file("a", 1)
    assert cs.get_n_largest("a", 10) == ["a(1)"]

@test(2)
def l2_no_matches(cs):
    cs.add_file("a", 1)
    assert cs.get_n_largest("zzz", 3) == []

@test(2)
def l2_deleted_excluded(cs):
    cs.add_file("p/a", 9); cs.add_file("p/b", 8)
    cs.delete_file("p/a")
    assert cs.get_n_largest("p/", 2) == ["p/b(8)"]

@test(2)
def l2_empty_prefix_matches_all(cs):
    cs.add_file("b", 2); cs.add_file("a", 3)
    assert cs.get_n_largest("", 5) == ["a(3)", "b(2)"]

@test(2)
def l2_n_zero(cs):
    cs.add_file("a", 1)
    assert cs.get_n_largest("", 0) == []


# ============================================================ NIVEL 3
@test(3)
def l3_add_user(cs):
    assert cs.add_user("u1", 100) is True
    assert cs.add_user("u1", 50) is False
    assert cs.add_user("admin", 10) is False, "admin existe desde el inicio"

@test(3)
def l3_add_file_by_returns_remaining(cs):
    cs.add_user("u1", 100)
    assert cs.add_file_by("u1", "f1", 30) == 70
    assert cs.add_file_by("u1", "f2", 20) == 50
    assert cs.get_file_size("f2") == 20

@test(3)
def l3_over_capacity(cs):
    cs.add_user("u1", 10)
    assert cs.add_file_by("u1", "big", 11) is None
    assert cs.get_file_size("big") is None, "un add fallido no debe dejar rastro"
    assert cs.add_file_by("u1", "ok", 4) == 6

@test(3)
def l3_exact_capacity(cs):
    cs.add_user("u1", 10)
    assert cs.add_file_by("u1", "f", 10) == 0

@test(3)
def l3_missing_user(cs):
    assert cs.add_file_by("ghost", "f", 1) is None
    assert cs.get_file_size("f") is None

@test(3)
def l3_duplicate_name_any_owner(cs):
    cs.add_user("u1", 100)
    cs.add_file("shared", 5)
    assert cs.add_file_by("u1", "shared", 1) is None
    assert cs.get_file_size("shared") == 5

@test(3)
def l3_delete_frees_capacity(cs):
    cs.add_user("u1", 10)
    cs.add_file_by("u1", "a", 8)
    assert cs.delete_file("a") == 8
    assert cs.add_file_by("u1", "b", 10) == 0

@test(3)
def l3_admin_unlimited(cs):
    assert cs.add_file("huge", 10**12) is True
    assert cs.add_file("huge2", 10**12) is True

@test(3)
def l3_add_file_by_admin_invalid(cs):
    assert cs.add_file_by("admin", "f", 1) is None

@test(3)
def l3_merge_basic(cs):
    cs.add_user("t", 50); cs.add_user("s", 30)
    cs.add_file_by("t", "t1", 10)
    cs.add_file_by("s", "s1", 5)
    assert cs.merge_user("t", "s") == 65          # (50+30) - (10+5)
    assert cs.add_file_by("s", "x", 1) is None, "el usuario origen ya no existe"
    assert cs.add_file_by("t", "t2", 65) == 0
    assert cs.get_file_size("s1") == 5

@test(3)
def l3_merge_source_id_reusable(cs):
    cs.add_user("t", 10); cs.add_user("s", 10)
    cs.merge_user("t", "s")
    assert cs.add_user("s", 3) is True

@test(3)
def l3_merge_invalid(cs):
    cs.add_user("a", 10)
    assert cs.merge_user("a", "a") is None
    assert cs.merge_user("a", "ghost") is None
    assert cs.merge_user("ghost", "a") is None
    assert cs.merge_user("a", "admin") is None
    assert cs.merge_user("admin", "a") is None
    assert cs.add_file_by("a", "f", 10) == 0, "un merge inválido no modifica nada"

@test(3)
def l3_merged_file_delete_frees_target(cs):
    cs.add_user("t", 10); cs.add_user("s", 10)
    cs.add_file_by("s", "s1", 10)
    cs.merge_user("t", "s")
    cs.delete_file("s1")
    assert cs.add_file_by("t", "big", 20) == 0

@test(3)
def l3_get_n_largest_still_works(cs):
    cs.add_user("u", 100)
    cs.add_file_by("u", "d/x", 40); cs.add_file("d/y", 60)
    assert cs.get_n_largest("d/", 2) == ["d/y(60)", "d/x(40)"]


# ============================================================ NIVEL 4
@test(4)
def l4_backup_count(cs):
    cs.add_user("u", 100)
    cs.add_file_by("u", "a", 1); cs.add_file_by("u", "b", 2)
    assert cs.backup_user("u") == 2
    assert cs.backup_user("ghost") is None
    assert cs.backup_user("admin") is None

@test(4)
def l4_restore_state(cs):
    cs.add_user("u", 100)
    cs.add_file_by("u", "a", 10)
    cs.backup_user("u")
    cs.delete_file("a")
    cs.add_file_by("u", "b", 20)
    assert cs.restore_user("u") == 1
    assert cs.get_file_size("a") == 10
    assert cs.get_file_size("b") is None, "archivos posteriores al backup se eliminan"
    assert cs.add_file_by("u", "c", 90) == 0, "la capacidad usada debe ser coherente"

@test(4)
def l4_restore_without_backup(cs):
    cs.add_user("u", 100)
    cs.add_file_by("u", "a", 10)
    assert cs.restore_user("u") == 0
    assert cs.get_file_size("a") is None
    assert cs.restore_user("ghost") is None

@test(4)
def l4_backup_overwrites(cs):
    cs.add_user("u", 100)
    cs.add_file_by("u", "a", 1)
    cs.backup_user("u")
    cs.add_file_by("u", "b", 2)
    assert cs.backup_user("u") == 2
    cs.delete_file("a"); cs.delete_file("b")
    assert cs.restore_user("u") == 2

@test(4)
def l4_restore_skips_taken_names(cs):
    cs.add_user("u", 100); cs.add_user("v", 100)
    cs.add_file_by("u", "a", 5); cs.add_file_by("u", "b", 6)
    cs.backup_user("u")
    cs.delete_file("a")
    cs.add_file_by("v", "a", 50)
    assert cs.restore_user("u") == 1
    assert cs.get_file_size("a") == 50, "el archivo de v no se toca"
    assert cs.get_file_size("b") == 6

@test(4)
def l4_backup_isolated_from_changes(cs):
    cs.add_user("u", 100)
    cs.add_file_by("u", "a", 5)
    cs.backup_user("u")
    cs.delete_file("a")
    cs.add_file_by("u", "a", 70)   # mismo nombre, otro tamaño
    assert cs.restore_user("u") == 1
    assert cs.get_file_size("a") == 5

@test(4)
def l4_merge_discards_source_backup(cs):
    cs.add_user("t", 10); cs.add_user("s", 10)
    cs.add_file_by("s", "s1", 3)
    cs.backup_user("s")
    cs.merge_user("t", "s")
    cs.add_user("s", 10)
    assert cs.restore_user("s") == 0
    assert cs.get_file_size("s1") == 3, "s1 ahora es de t y no se toca"

@test(4)
def l4_merge_keeps_target_backup(cs):
    cs.add_user("t", 10); cs.add_user("s", 10)
    cs.add_file_by("t", "t1", 4)
    cs.backup_user("t")
    cs.add_file_by("s", "s1", 3)
    cs.merge_user("t", "s")
    assert cs.restore_user("t") == 1
    assert cs.get_file_size("t1") == 4
    assert cs.get_file_size("s1") is None, "restore borra todo lo actual de t, incluido lo fusionado"
    assert cs.add_file_by("t", "z", 16) == 0, "capacidad = 20 tras el merge, usado = 4"

@test(4)
def l4_restore_idempotent(cs):
    cs.add_user("u", 100)
    cs.add_file_by("u", "a", 1); cs.add_file_by("u", "b", 2)
    cs.backup_user("u")
    assert cs.restore_user("u") == 2
    assert cs.restore_user("u") == 2
    assert cs.get_n_largest("", 5) == ["b(2)", "a(1)"]

@test(4)
def l4_backup_empty_user(cs):
    cs.add_user("u", 10)
    assert cs.backup_user("u") == 0
    cs.add_file_by("u", "a", 1)
    assert cs.restore_user("u") == 0
    assert cs.get_file_size("a") is None


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
    parser.add_argument("path", nargs="?", default="cloud_storage_inicio-2.py")
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
                fn(module.CloudStorage())
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
