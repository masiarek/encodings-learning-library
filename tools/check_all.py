#!/usr/bin/env python3
"""Run every gate CI runs, in CI's order, and report honestly.

Why this exists rather than four commands in a row.

A gate is only useful if you notice it failed, and the usual way of running one
by hand hides exactly that:

    python3 tools/run_examples.py --check 2>&1 | tail -1

A pipeline's exit status is the LAST command's, so `tail` reports success no
matter what the gate said. The pipe is there for a good reason — these gates
print a line per example and you want the summary — and the cost is that a red
gate scrolls past under a green-looking last line. `set -o pipefail` fixes it;
remembering to type it every time does not. And the array lookup people reach
for instead is shell-specific: `${PIPESTATUS[0]}` is bash's spelling, and under
zsh -- which is what runs here -- it quietly expands to the empty string rather
than erroring, so it prints `exit=` and reads like a stumble instead of a wrong
answer. (zsh's own array is lowercase and 1-indexed: `${pipestatus[1]}`.) That
is the same failure one level down, which is the argument for not piping at all.

So: no pipes here. Each gate runs through subprocess, its status is kept, its
output is shown only when it fails, and this script exits non-zero if any of
them did.

    python3 tools/check_all.py              # the working tree
    python3 tools/check_all.py --committed  # what CI will actually see
    python3 tools/check_all.py --selftest   # prove a failure is still reported

--committed is the one worth knowing about. CI checks out the commit, not your
directory, and the two differ in both directions: an untracked file makes your
tree red where CI is green (someone else's half-built lesson), and an untracked
file that a committed page LINKS to makes CI red where your tree is green. This
flag extracts HEAD into a temporary directory and runs the gates there.
"""

from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent

# Exactly what .github/workflows/{examples,docs}.yml run, in the same order.
GATES: list[tuple[str, list[str]]] = [
    ("examples", [sys.executable, "tools/run_examples.py", "--check"]),
    ("link style", [sys.executable, "tools/check_link_style.py"]),
    ("decomposed selftest", [sys.executable, "tools/check_decomposed_literals.py", "--selftest"]),
    ("decomposed", [sys.executable, "tools/check_decomposed_literals.py"]),
    # CI does `uv sync --group docs` first; `uv run --group docs` is the same
    # resolution in one step, and it is what makes this work in the temporary
    # directory --committed extracts into, where no .venv exists yet.
    ("mkdocs --strict", ["uv", "run", "--group", "docs", "mkdocs", "build", "--strict"]),
]


def run_gates(root: pathlib.Path, label: str) -> int:
    print(f"gates on {label}: {root}\n")
    failed: list[str] = []
    for name, cmd in GATES:
        if shutil.which(cmd[0]) is None:
            print(f"  SKIP  {name:<22} ({cmd[0]} not on PATH)")
            continue
        done = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
        if done.returncode == 0:
            print(f"  ok    {name}")
            continue
        failed.append(name)
        print(f"  FAIL  {name:<22} exit {done.returncode}")
        # Drop the per-item "ok" lines: on a failure they are the part you do
        # not need, and they crowd out the part you do.
        noise = (done.stdout + done.stderr).rstrip().split("\n")
        signal = [ln for ln in noise if not ln.lstrip().startswith("ok ")] or noise
        for line in signal[-12:]:
            print(f"          {line}")
    print()
    if failed:
        print(f"{len(failed)} gate(s) failed: {', '.join(failed)}")
        return 1
    print(f"all {len(GATES)} gates pass.")
    return 0


def committed_tree() -> int:
    """Run the gates against `git archive HEAD`, which is what CI checks out."""
    with tempfile.TemporaryDirectory() as tmp:
        archive = subprocess.run(
            ["git", "archive", "HEAD"], cwd=REPO, capture_output=True, check=True
        )
        subprocess.run(["tar", "-x", "-C", tmp], input=archive.stdout, check=True)
        head = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=REPO, capture_output=True, text=True
        ).stdout.strip()
        return run_gates(pathlib.Path(tmp), f"the committed tree ({head})")


def selftest() -> int:
    """A failing gate must be reported as failing. Proves this script still bites."""
    global GATES
    GATES = [("deliberate failure", [sys.executable, "-c", "raise SystemExit(3)"])]
    print("selftest: running one gate that exits 3\n")
    if run_gates(REPO, "the working tree") == 0:
        print("SELFTEST FAILED: a failing gate was reported as passing.")
        return 1
    print("selftest passed: the failure was reported.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--committed", action="store_true", help="run against git archive HEAD")
    parser.add_argument("--selftest", action="store_true", help="prove a failure is reported")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if args.committed:
        return committed_tree()
    return run_gates(REPO, "the working tree")


if __name__ == "__main__":
    sys.exit(main())
