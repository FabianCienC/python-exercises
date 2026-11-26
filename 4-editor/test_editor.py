"""
Tests por nivel para el ejercicio Editor de texto.

Uso (funciona aunque los archivos sean .txt):
    python test_editor.txt editor_inicio.py              # todos los niveles
    python test_editor.txt editor_inicio.py --nivel 2    # solo hasta L2
    python test_editor.txt editor_inicio.py -v           # detalle de cada fallo

Cada test crea una instancia nueva de TextEditor.
"""

import argparse
import importlib.machinery
import importlib.util
import sys
import traceback

DEFAULT_PATH = "editor_inicio.py"
CLASS_NAME = "TextEditor"
TESTS = {1: [], 2: [], 3: [], 4: []}


def test(level):
    def deco(fn):
        TESTS[level].append(fn)
        return fn
    return deco


# ============================================================ NIVEL 1
@test(1)
def l1_insert_returns_text(e):
    assert e.insert("hola") == "hola"
    assert e.insert(" mundo") == "hola mundo"

@test(1)
def l1_get_text(e):
    assert e.get_text() == ""
    e.insert("abc")
    assert e.get_text() == "abc"

@test(1)
def l1_insert_at_cursor(e):
    e.insert("ab")
    assert e.move_cursor(1) == "ab"
    assert e.insert("X") == "aXb"
    assert e.insert("Y") == "aXYb", "el cursor queda después de lo insertado"

@test(1)
def l1_move_cursor_clamps(e):
    e.insert("abc")
    e.move_cursor(-5)
    assert e.insert("0") == "0abc"
    e.move_cursor(100)
    assert e.insert("!") == "0abc!"

@test(1)
def l1_backspace(e):
    e.insert("abc")
    assert e.backspace() == "ab"
    e.move_cursor(1)
    assert e.backspace() == "b"

@test(1)
def l1_backspace_at_start(e):
    e.insert("abc")
    e.move_cursor(0)
    assert e.backspace() == "abc"
    assert e.insert("Z") == "Zabc"

@test(1)
def l1_backspace_empty(e):
    assert e.backspace() == ""
    assert e.insert("a") == "a"


# ============================================================ NIVEL 2
@test(2)
def l2_select_insert_replaces(e):
    e.insert("hola mundo")
    e.select(5, 10)
    assert e.insert("Fabian") == "hola Fabian"
    assert e.insert("!") == "hola Fabian!", "el cursor queda al final de lo insertado"

@test(2)
def l2_select_backspace_deletes(e):
    e.insert("abcdef")
    e.select(1, 4)
    assert e.backspace() == "aef"
    assert e.insert("X") == "aXef", "el cursor queda donde empezaba la selección"

@test(2)
def l2_select_clamps_and_swaps(e):
    e.insert("abcdef")
    e.select(10, 3)                     # -> [3, 6)
    assert e.backspace() == "abc"

@test(2)
def l2_select_empty_is_move(e):
    e.insert("abc")
    e.select(1, 1)
    assert e.insert("X") == "aXbc"

@test(2)
def l2_move_clears_selection(e):
    e.insert("abc")
    e.select(0, 2)
    e.move_cursor(3)
    assert e.insert("Z") == "abcZ", "mover el cursor quita la selección"

@test(2)
def l2_copy_paste(e):
    e.insert("abc")
    e.select(0, 2)
    assert e.copy() == "abc", "copy no modifica el texto"
    e.move_cursor(3)
    assert e.paste() == "abcab"
    assert e.paste() == "abcabab"

@test(2)
def l2_paste_replaces_selection(e):
    e.insert("hello world")
    e.select(0, 5)
    e.copy()
    e.select(6, 11)
    assert e.paste() == "hello hello"

@test(2)
def l2_copy_without_selection_keeps_clipboard(e):
    e.insert("xy")
    e.select(0, 1)
    e.copy()
    e.move_cursor(2)
    e.copy()                             # sin selección: no cambia el portapapeles
    assert e.paste() == "xyx"

@test(2)
def l2_paste_empty_clipboard(e):
    e.insert("abc")
    assert e.paste() == "abc"


# ============================================================ NIVEL 3
@test(3)
def l3_undo_insert(e):
    e.insert("ab")
    e.insert("cd")
    assert e.undo() == "ab"
    assert e.undo() == ""

@test(3)
def l3_undo_backspace(e):
    e.insert("abc")
    e.backspace()
    assert e.undo() == "abc"

@test(3)
def l3_undo_restores_cursor(e):
    e.insert("abc")
    e.move_cursor(1)
    e.insert("X")                        # aXbc, cursor 2
    e.undo()                             # abc, cursor 1
    assert e.insert("Y") == "aYbc"

@test(3)
def l3_undo_restores_selection(e):
    e.insert("hola mundo")
    e.select(5, 10)
    e.insert("X")
    assert e.undo() == "hola mundo"
    assert e.insert("Y") == "hola Y", "la selección vuelve a estar activa"

@test(3)
def l3_redo(e):
    e.insert("a")
    e.insert("b")
    e.undo(); e.undo()
    assert e.redo() == "a"
    assert e.redo() == "ab"
    assert e.redo() == "ab", "sin nada que rehacer no cambia"

@test(3)
def l3_new_edit_clears_redo(e):
    e.insert("a")
    e.insert("b")
    e.undo()
    e.insert("c")
    assert e.redo() == "ac"

@test(3)
def l3_undo_empty(e):
    assert e.undo() == ""
    e.insert("a")
    e.undo()
    assert e.undo() == ""

@test(3)
def l3_non_edits_not_recorded(e):
    e.insert("abc")
    e.move_cursor(1)
    e.select(0, 2)
    e.copy()
    e.move_cursor(0)
    e.backspace()                        # no borra nada: no se registra
    assert e.undo() == "", "undo deshace el último cambio real de texto"

@test(3)
def l3_undo_paste(e):
    e.insert("ab")
    e.select(0, 2)
    e.copy()
    e.move_cursor(2)
    e.paste()
    assert e.undo() == "ab"
    assert e.redo() == "abab"


# ============================================================ NIVEL 4
@test(4)
def l4_default_and_create(e):
    e.insert("main")
    assert e.create_document("notas") is True
    assert e.create_document("notas") is False
    assert e.create_document("default") is False, "el documento inicial se llama default"

@test(4)
def l4_switch(e):
    e.insert("main")
    e.create_document("b")
    assert e.switch_document("b") is True
    assert e.get_text() == ""
    e.insert("bee")
    e.switch_document("default")
    assert e.get_text() == "main"
    assert e.switch_document("ghost") is False
    assert e.get_text() == "main"

@test(4)
def l4_cursor_per_document(e):
    e.insert("abc")
    e.move_cursor(1)
    e.create_document("b")
    e.switch_document("b")
    e.insert("zz")
    e.switch_document("default")
    assert e.insert("X") == "aXbc", "cada documento conserva su cursor"

@test(4)
def l4_selection_per_document(e):
    e.insert("hola")
    e.select(0, 4)
    e.create_document("b")
    e.switch_document("b")
    e.insert("x")
    e.switch_document("default")
    assert e.insert("Y") == "Y", "cada documento conserva su selección"

@test(4)
def l4_history_per_document(e):
    e.insert("a")
    e.create_document("b")
    e.switch_document("b")
    e.insert("bb")
    e.switch_document("default")
    assert e.undo() == ""
    e.switch_document("b")
    assert e.get_text() == "bb"
    assert e.undo() == ""

@test(4)
def l4_clipboard_shared(e):
    e.insert("copiar")
    e.select(0, 6)
    e.copy()
    e.create_document("b")
    e.switch_document("b")
    assert e.paste() == "copiar"

@test(4)
def l4_delete(e):
    e.create_document("b")
    assert e.delete_document("ghost") is False
    assert e.delete_document("default") is False, "no se puede borrar el activo"
    assert e.delete_document("b") is True
    assert e.switch_document("b") is False

@test(4)
def l4_recreate_is_empty(e):
    e.create_document("b")
    e.switch_document("b")
    e.insert("viejo")
    e.switch_document("default")
    e.delete_document("b")
    e.create_document("b")
    e.switch_document("b")
    assert e.get_text() == ""
    assert e.undo() == "", "sin historial del documento anterior"


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
