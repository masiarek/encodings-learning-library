#!/usr/bin/env python3
"""Run every card snippet; diff its stdout against the card's `expect`.

Same contract as the library's own `tools/run_examples.py`, and for the same
reason: a card must not be able to claim output no program produced. The one
difference is that a card is not a lesson page, so the snippets live inside
`cards_*.py` rather than in `examples/`, and this tool writes them out to a
scratch directory before running them.

Four kinds of snippet, named by the card's `lang`:

    py   stdlib-only Python, run as `python3 -I <file>.py`
    rs   compiled with `rustc --edition 2024`, no cargo, no crates
    sh   run as `bash <file>.sh` -- xxd, od, printf
    c    compiled with `cc -std=c11 -Wall -Wextra`, no libraries

Every snippet runs under one fixed environment -- LC_ALL=C, LANG=C,
PYTHONUTF8=1 -- so the answer key does not depend on whoever ran it.

A card may also claim that its snippet does NOT build:

    fails="E0308"          a rustc error code, matched against [Exxxx] in stderr
    fails_msg="out of range hex escape"    a substring, for the errors rustc and
                                           cc issue with no code at all

    python3 verify.py               all card modules
    python3 verify.py cards_hex     just this one
"""

from __future__ import annotations

import importlib.util
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
SNIP = HERE / "snippets"
BIN = HERE / "bin"
EDITION = "2024"
MODULES = ["cards_hex"]

ENV = {**os.environ, "LC_ALL": "C", "LANG": "C", "PYTHONUTF8": "1"}


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def build_cmd(lang, src, binary):
    if lang == "rs":
        return ["rustc", "--edition", EDITION, str(src), "-o", str(binary)]
    if lang == "c":
        return ["cc", "-std=c11", "-Wall", "-Wextra", str(src), "-o", str(binary)]
    return None


def run_cmd(lang, src, binary):
    if lang == "py":
        return [sys.executable, "-I", str(src)]
    if lang == "sh":
        return ["bash", str(src)]
    return [str(binary)]


def check(card):
    """-> (status, detail).  status in {ok, skip, MISMATCH, BUILD-FAIL, WRONG-ERROR, RUNTIME}"""
    code = card.get("code")
    if not code:
        return ("skip", "no code")

    lang = card["lang"]
    src = SNIP / f"{card['id']}.{lang}"
    src.write_text(code + "\n", encoding="utf-8")
    binary = BIN / card["id"]

    want_fail = card.get("fails")
    want_msg = card.get("fails_msg")

    build = build_cmd(lang, src, binary)
    if build is not None:
        r = subprocess.run(build, capture_output=True, text=True, env=ENV)
        if want_fail or want_msg:
            if r.returncode == 0:
                claim = want_fail or repr(want_msg)
                return ("WRONG-ERROR", f"expected to fail with {claim}, but it BUILT")
            if want_fail:
                codes = sorted(set(re.findall(r"\[(E\d{4})\]", r.stderr)))
                if want_fail not in codes:
                    first = next((l for l in r.stderr.splitlines() if l.startswith("error")), "")
                    return ("WRONG-ERROR", f"expected {want_fail}, got {codes or 'none'} | {first}")
                return ("ok", f"fails with {want_fail} as claimed")
            if want_msg not in r.stderr:
                first = next((l for l in r.stderr.splitlines() if l.startswith("error")), "")
                return ("WRONG-ERROR", f"expected {want_msg!r} in stderr | {first}")
            return ("ok", f"fails with {want_msg!r} as claimed")
        if r.returncode != 0:
            return ("BUILD-FAIL", "\n".join(r.stderr.splitlines()[:6]))
    elif want_fail or want_msg:
        return ("WRONG-ERROR", f"{lang} is not compiled; a fails= card needs rs or c")

    run = subprocess.run(
        run_cmd(lang, src, binary), capture_output=True, text=True, timeout=60, env=ENV
    )
    if run.returncode != 0:
        return ("RUNTIME", f"exit {run.returncode}: {run.stderr.strip()[:300]}")
    got = run.stdout.rstrip("\n")
    want = (card.get("expect") or "").rstrip("\n")
    if got != want:
        return ("MISMATCH", f"want {want!r}\n         got  {got!r}")
    return ("ok", "")


def main(modules):
    SNIP.mkdir(exist_ok=True)
    BIN.mkdir(exist_ok=True)
    bad = 0
    for name in modules:
        m = load(name)
        print(f"\n=== {name} ({len(m.CARDS)} cards) ===")
        for card in m.CARDS:
            status, detail = check(card)
            if status == "ok":
                print(f"  ok       {card['id']}" + (f"  ({detail})" if detail else ""))
            elif status == "skip":
                print(f"  --       {card['id']}  (prose only)")
            else:
                bad += 1
                print(f"  {status:<11} {card['id']}\n         {detail}")
    print(f"\n{'ALL VERIFIED' if not bad else str(bad) + ' PROBLEM(S)'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or MODULES))
