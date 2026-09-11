#!/usr/bin/env python3
"""Run every gate CI runs, in CI's order, and report honestly.

Why this exists rather than the gates typed one after another.

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

And a gate that did not RUN is not a gate that passed. A gate whose executable
is not on PATH is skipped -- the last three start with `uv`, so a machine
without it skips all three -- and until 2026-09-10 a skip was counted nowhere:
the run printed SKIP, then `all 11 gates pass.` and exit 0, after running
eight. That is the false green this script exists to prevent, and neither the
status nor the summary gave a hint of it. So the summary now says how many
gates RAN, names any that did not, and says `all N gates` only when all N did;
and a skip exits 1, as a failure does. It has to be the status and not just the
text, because the status is what a script -- or a hurried reader -- checks, and
0 is a claim that every gate has a verdict. `--allow-skip` is the opt-out, for
a machine that genuinely cannot run a gate: if nothing that ran failed it exits
0, but the summary still says `8 of 11 gates ran`. Accepting a partial verdict
should cost a flag, not happen to you.

    python3 tools/check_all.py              # the working tree
    python3 tools/check_all.py --staged     # the tree your next commit makes
    python3 tools/check_all.py --committed  # what CI will actually see
    python3 tools/check_all.py --mine A B   # HEAD, plus only the paths you name
    python3 tools/check_all.py --selftest   # prove a failure, or a skip, is reported

--committed is the one worth knowing about. CI checks out the commit, not your
directory, and the two differ in both directions: an untracked file makes your
tree red where CI is green (someone else's half-built lesson), and an untracked
file that a committed page LINKS to makes CI red where your tree is green. This
flag extracts HEAD into a temporary directory and runs the gates there.

--staged is the one between them, and it is the one to run immediately before
committing. --committed archives HEAD and so cannot see the index at all: it is
green and says nothing about the commit you are about to make. --staged writes
the index out with `git write-tree` and gates that. In a checkout several
sessions share, that gap is where the damage happens -- `git add` on a shared
file takes a colleague's in-flight lines with it.

--mine is the one for UNCOMMITTED work while somebody else is mid-edit, and it
is the only mode that isolates you. The bare working-tree run reads their
unstaged edits; --staged writes out the shared INDEX, so their `git add` enters
your verdict; --committed cannot see uncommitted work at all. Each is green or
red for reasons that are not yours. --mine extracts HEAD and copies in only the
paths you name, so what it gates is HEAD plus your work and nothing else.

You must name the paths. Inferring them from `git status` reproduces the bug:
on 2026-09-07 a half-applied rename left one session's tree showing six
deletions and an addition belonging to ANOTHER session, and anything that
overlaid everything dirty would have gated a colleague's in-flight work as
yours and called it green. Being made to say what you are claiming is half the
value of the mode.

And each path you name must exist somewhere: in your tree, or in HEAD, where
its absence from your tree makes it a deletion. Until 2026-09-10 a path in
neither was noted SKIPPED and the run went on. `--mine 06_Terminal/my_lesonn`,
for a lesson called `my_lesson`, gated HEAD plus nothing of yours and exited 0
whenever HEAD was green. That is the skipped-gate hole one level up: every
gate ran, but on a tree your work was not in, so the 0 was a verdict on your
work that nobody had. So a path in neither place now refuses the run before
any gate starts, naming the path, with exit 2 -- argparse's code for a usage
error.

Refusing is safe because such a path can change nothing in the tree being
gated: your tree has nothing to copy in, and HEAD has nothing to remove. The
only way to name one without a mistake -- a typo, or a path written from the
directory you stand in rather than from the repository root -- is to name a
file created and deleted without ever being committed, or one whose deletion
is already committed, and naming either is a no-op. So the refusal costs you
nothing but a name that did nothing.

And each path you name must land inside the repository, because until
2026-09-10 one that did not could delete your work. A path is read from
`repo / path` and written to `dest / path`, and pathlib's `/` returns an
absolute right-hand side unchanged: for `--mine "$PWD/06_Terminal/my_lesson"`,
which is what tab completion writes, both were the lesson itself. Mirroring a
directory clears the destination before copying, so the run deleted the real
lesson, uncommitted work and all, then crashed with nothing left to copy. A
path climbing out with `..` escaped the same way, reading from beside the
repository and writing beside the temporary tree.

So every path is settled before anything is extracted, by where it lands:
joined onto the root if relative, as it stands if absolute, resolved either
way. Inside the repository it is used as a path from the root, which converts
an absolute one. Converting is not a guess -- an absolute path names exactly
one file -- and it lets the path tab completion writes simply work. Anywhere
else refuses the run with exit 2, and so does the root itself: naming it
claims your whole working tree, colleagues' edits included, which is the bare
run and the opposite of what --mine is for.
"""

from __future__ import annotations

import argparse
import contextlib
import io
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
    ("katas selftest", [sys.executable, "tools/check_katas.py", "--selftest"]),
    ("katas", [sys.executable, "tools/check_katas.py"]),
    ("chapter status selftest",
     [sys.executable, "tools/check_chapter_status.py", "--selftest"]),
    ("chapter status", [sys.executable, "tools/check_chapter_status.py"]),
    # CI does `uv sync --group docs` first; `uv run --group docs` is the same
    # resolution in one step, and it is what makes this work in the temporary
    # directory --committed extracts into, where no .venv exists yet.
    ("nav chain selftest",
     ["uv", "run", "--group", "docs", "python", "tools/check_nav_chain.py", "--selftest"]),
    ("nav chain", ["uv", "run", "--group", "docs", "python", "tools/check_nav_chain.py"]),
    ("mkdocs --strict", ["uv", "run", "--group", "docs", "mkdocs", "build", "--strict"]),
]


def run_gates(root: pathlib.Path, label: str, allow_skip: bool = False) -> int:
    print(f"gates on {label}: {root}\n")
    failed: list[str] = []
    skipped: list[str] = []
    missing: list[str] = []  # the executables behind the skips, for the advice line
    for name, cmd in GATES:
        if shutil.which(cmd[0]) is None:
            print(f"  SKIP  {name:<22} ({cmd[0]} not on PATH)")
            skipped.append(name)
            if cmd[0] not in missing:
                missing.append(cmd[0])
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
    total, ran = len(GATES), len(GATES) - len(skipped)
    if not failed and not skipped:
        print(f"all {total} gates ran and passed.")
        return 0
    # From here on a gate failed or never ran, so the summary counts from what
    # RAN and never says "all": a skip counted nowhere is how this line once
    # read `all 11 gates pass.` after running eight.
    summary = f"{ran} of {total} gates ran"
    summary += f"; {len(failed)} failed: {', '.join(failed)}" if failed else " and passed"
    if skipped:
        summary += f"; {len(skipped)} skipped: {', '.join(skipped)}"
    print(summary + ".")
    if failed:
        return 1
    if allow_skip:
        print(f"--allow-skip: exit 0, but the {len(skipped)} skipped gate(s) have no verdict.")
        return 0
    print(f"NOT a pass: a gate that did not run has no verdict. Put {', '.join(missing)} "
          "on PATH, or rerun with --allow-skip to accept a partial run.")
    return 1


def committed_tree(allow_skip: bool = False) -> int:
    """Run the gates against `git archive HEAD`, which is what CI checks out."""
    with tempfile.TemporaryDirectory() as tmp:
        archive = subprocess.run(
            ["git", "archive", "HEAD"], cwd=REPO, capture_output=True, check=True
        )
        subprocess.run(["tar", "-x", "-C", tmp], input=archive.stdout, check=True)
        head = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=REPO, capture_output=True, text=True
        ).stdout.strip()
        return run_gates(pathlib.Path(tmp), f"the committed tree ({head})", allow_skip)


def staged_tree(allow_skip: bool = False) -> int:
    """Run the gates against the tree your NEXT commit would produce.

    --committed archives HEAD, so it cannot see the index -- which means it is
    green and uninformative at exactly the moment it matters, the moment before
    you commit. In a checkout several sessions write to, the difference is not
    academic: `git add <shared file>` picks up whatever a colleague has left in
    it, and a row pointing at a folder they have not committed yet passes
    `mkdocs build --strict` (a stale NAV_ORDER name is a silent no-op, not a
    broken link) while failing check_nav_chain. Observed twice on 2026-09-07,
    once against the author of that gate.

    `git write-tree` writes the current index out as a tree object. It reads
    the index and moves no ref, so it is safe to run while others are working.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tree = subprocess.run(
            ["git", "write-tree"], cwd=REPO, capture_output=True, text=True, check=True
        ).stdout.strip()
        archive = subprocess.run(
            ["git", "archive", tree], cwd=REPO, capture_output=True, check=True
        )
        subprocess.run(["tar", "-x", "-C", tmp], input=archive.stdout, check=True)
        return run_gates(pathlib.Path(tmp), f"the staged tree ({tree[:7]})", allow_skip)


def repo_relative(repo: pathlib.Path, named: str) -> str | None:
    """Where `named` lands, as a path from `repo`'s root -- or None unless strictly inside it.

    `repo / named` is where it points, whichever kind it is: pathlib joins a
    relative path onto the root and takes an absolute one as it stands -- the
    behaviour behind the deletion, harmless here because the result is judged
    before anything uses it. Both sides are resolved, `..` and symlinks with
    them, because REPO is resolved and a path you type need not be: on macOS
    /tmp is /private/tmp.
    """
    path, root = (repo / named).resolve(), repo.resolve()
    if path == root or not path.is_relative_to(root):
        return None
    return str(path.relative_to(root))


def assemble_mine(repo: pathlib.Path, paths: list[str],
                  dest: pathlib.Path) -> tuple[list[str], list[str], list[str]]:
    """Extract HEAD into `dest`, then overlay only `paths` from the working tree.

    Returns (notes, outside, unknown). The notes say what it did, one line per
    path, so the run says out loud whose work is being gated. A named path
    that is gone from the working tree is a DELETION and is removed from the
    tree -- deleting a file is work too, and a mode that silently kept it would
    pass a commit that CI then fails on.

    `outside` is the named paths that do not land inside the repository, found
    before anything is extracted; if there are any, nothing else is done. The
    rest are used as repo_relative gives them, so an absolute path inside the
    repository is converted, and the notes name what it became.

    `unknown` is the named paths that are in neither the working tree nor HEAD.
    If there are any, nothing is overlaid and there are no notes. mine_tree
    refuses a run with either, so there is no tree worth building.
    """
    rels = [repo_relative(repo, named) for named in paths]
    outside = [named for named, rel in zip(paths, rels) if rel is None]
    if outside:
        return [], outside, []

    archive = subprocess.run(
        ["git", "archive", "HEAD"], cwd=repo, capture_output=True, check=True
    )
    subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout, check=True)

    # Decided against HEAD as extracted, before anything is overlaid: once a
    # named directory is mirrored, a file deleted inside it is missing from both
    # sides, and would read as unknown when it is a deletion.
    unknown = [rel for rel in rels if not (repo / rel).exists() and not (dest / rel).exists()]
    if unknown:
        return [], [], unknown

    notes: list[str] = []
    for rel in rels:
        src, dst = repo / rel, dest / rel
        if src.is_dir():
            # REPLACE, do not merge. copytree(dirs_exist_ok=True) unions your
            # tree onto HEAD, so a file deleted *inside* a named directory
            # survives from HEAD and the gate passes a tree that cannot exist
            # -- a false green, in the dangerous direction. Retiring an example
            # is the live case: drop foo_py.py and foo_py.out, miss the page's
            # `<!-- output:foo_py -->`, and the real committed tree fails
            # run_examples while a merged tree still has the file sitting there.
            # dst may be absent when the directory is new in your tree.
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            notes.append(f"overlaid dir   {rel}  (mirrored, deletions included)")
        elif src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            notes.append(f"overlaid file  {rel}")
        elif dst.is_dir():
            shutil.rmtree(dst)
            notes.append(f"removed dir    {rel}  (deleted in your tree)")
        elif dst.is_file():
            dst.unlink()
            notes.append(f"removed file   {rel}  (deleted in your tree)")
        else:
            # In HEAD, or it would be unknown, but gone from `dest` already: a
            # path named before it -- a directory above it, or itself -- took it.
            notes.append(f"already gone   {rel}  (deleted in your tree)")
    return notes, [], []


def refuse_mine(named: list[str], why: str, advice: list[str]) -> int:
    """Name on stderr the paths that refused a --mine run, say why, and return exit 2."""
    lines = [f"  REFUSED        {rel}  ({why})" for rel in named]
    print("\n".join(lines + [""] + advice), file=sys.stderr)
    return 2


def mine_tree(paths: list[str], allow_skip: bool = False, repo: pathlib.Path = REPO) -> int:
    """Gate HEAD plus only the paths you name -- the honest check for uncommitted work.

    A named path that does not land inside the repository, or that is in
    neither your tree nor HEAD, refuses the whole run, exit 2, before any gate:
    the module docstring says why for each. `repo` is there for the selftest,
    which points this at a scratch repository.
    """
    with tempfile.TemporaryDirectory() as tmp:
        dest = pathlib.Path(tmp)
        notes, outside, unknown = assemble_mine(repo, paths, dest)
        if outside:
            return refuse_mine(outside, "not inside the repository", [
                "--mine refused, and nothing was extracted: it takes paths inside the "
                "repository and no others -- not its root either, which is your whole "
                "working tree.",
                f"Name them from the root, {repo}, or by an absolute path inside it."])
        if unknown:
            return refuse_mine(unknown, "not in your tree and not in HEAD", [
                "--mine refused, and no gate ran: a named path in neither place "
                "is probably a typo.",
                f"Relative paths are from the repository root, {repo}.",
                "If it is not a typo, drop it: naming it changes nothing in the tree "
                "that is gated."])
        for note in notes:
            print(f"  {note}")
        print()
        head = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=repo, capture_output=True, text=True
        ).stdout.strip()
        return run_gates(dest, f"HEAD ({head}) plus {len(paths)} path(s) of yours", allow_skip)


def selftest_mine() -> int:
    """Prove --mine gates your work and not a colleague's, and refuses a path it must not take.

    The first checks are about the TREE it assembles, not about running the
    real gates: those need uv, mkdocs and this repo's own content, so a
    three-way fixture that ran them would be testing the gates rather than the
    mode. What can be wrong here is which bytes end up in the tree, so that is
    what is checked -- in a scratch repo, touching nothing shared.

    The last are about the DECISION mine_tree makes, which no tree can show: a
    run that should be refused assembles a perfectly good one. So mine_tree
    itself runs on the same scratch repo, still without the real gates: GATES
    is swapped for one stand-in that copies the tree it is handed, so whether
    a gate ran, and what it saw, are observed rather than read off the output.
    First a CONTROL naming real work, deletions included, which must run the
    stand-in and exit 0 -- what makes the copy's absence afterwards a finding
    rather than a stand-in that never worked. Then the same paths plus one
    that is nowhere, which must exit 2 with the stand-in never run.

    Then the paths themselves. lesson/, holding an untracked draft git could
    never give back, is named by an absolute path through a symlink, as tab
    completion writes it in a checkout reached through one: the stand-in must
    see the draft, and lesson/ must still hold it afterwards -- until
    2026-09-10 that path deleted it. Then the real work plus three paths that
    do not land inside the repository, which must refuse the run and name
    exactly those three. Every tree these runs build is made inside this
    scratch directory, so were the deletion ever back, it would delete scratch.
    """
    global GATES
    print("selftest --mine: assembling HEAD + named paths in a scratch repo\n")
    with tempfile.TemporaryDirectory() as tmp:
        repo, dest = pathlib.Path(tmp) / "repo", pathlib.Path(tmp) / "out"
        repo.mkdir(); dest.mkdir()
        q = dict(cwd=repo, capture_output=True, check=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], **q)
        subprocess.run(["git", "config", "user.email", "t@t"], **q)
        subprocess.run(["git", "config", "user.name", "t"], **q)
        (repo / "mine.txt").write_text("committed\n")
        (repo / "theirs.txt").write_text("committed\n")
        (repo / "doomed.txt").write_text("committed\n")
        (repo / "lesson").mkdir()
        (repo / "lesson" / "keep.txt").write_text("committed\n")
        (repo / "lesson" / "retired.txt").write_text("committed\n")
        subprocess.run(["git", "add", "-A"], **q)
        subprocess.run(["git", "commit", "-qm", "base"], **q)

        # Now: my edit, a colleague's edit, my deletion, my untracked folder, and
        # an untracked draft inside lesson/, the kind of work git cannot give back.
        (repo / "mine.txt").write_text("MY EDIT\n")
        (repo / "theirs.txt").write_text("THEIR EDIT\n")
        (repo / "doomed.txt").unlink()
        (repo / "newdir").mkdir(); (repo / "newdir" / "n.txt").write_text("MY NEW FILE\n")
        (repo / "lesson" / "retired.txt").unlink()            # an example retired
        (repo / "lesson" / "keep.txt").write_text("MY EDIT\n")
        (repo / "lesson" / "draft.txt").write_text("MY DRAFT\n")
        subprocess.run(["git", "add", "theirs.txt"], **q)   # their `git add`, which --staged would swallow

        assemble_mine(repo, ["mine.txt", "doomed.txt", "newdir", "lesson"], dest)

        checks = [
            ("my edit is present", (dest / "mine.txt").read_text() == "MY EDIT\n"),
            ("their edit is NOT", (dest / "theirs.txt").read_text() == "committed\n"),
            ("my deletion applied", not (dest / "doomed.txt").exists()),
            ("my untracked file is present", (dest / "newdir" / "n.txt").exists()),
            # One level in: the case a MERGING copytree gets wrong, silently.
            ("deletion INSIDE a named dir applied",
             not (dest / "lesson" / "retired.txt").exists()),
            ("my edit inside that dir survived",
             (dest / "lesson" / "keep.txt").read_text() == "MY EDIT\n"),
        ]

        # The decision. Every kind of work is named, including two deletions a
        # refusal must not take for typos: doomed.txt, and lesson/retired.txt,
        # which is gone from the tree being built as well once `lesson` has
        # been mirrored into it.
        seen = pathlib.Path(tmp) / "what-the-gate-saw"
        GATES = [("stand-in", [sys.executable, "-c",
                               f"import shutil; shutil.copytree('.', {str(seen)!r})"])]
        work = ["mine.txt", "doomed.txt", "newdir", "lesson", "lesson/retired.txt"]
        typo = "lesonn"  # `lesson`, mistyped
        # lesson/ by an absolute path through a symlink, so that a conversion
        # comparing unresolved paths refuses it here, as it would in a checkout
        # reached through /tmp -- which on macOS is /private/tmp.
        alias = pathlib.Path(tmp) / "alias"
        alias.symlink_to(repo)
        by_abs = str(alias / "lesson")
        # Not inside the repository: a directory beside it, by absolute path and
        # by climbing out to it, and the root itself, spelled with `..`.
        elsewhere = pathlib.Path(tmp) / "elsewhere"
        elsewhere.mkdir(); (elsewhere / "precious.txt").write_text("NOT IN THE REPO\n")
        not_inside = [str(elsewhere), "../elsewhere", "lesson/.."]

        def holds(path: pathlib.Path, text: str) -> bool:
            return path.is_file() and path.read_text() == text

        runs = []
        # From here on mine_tree makes its tree in this scratch directory, beside
        # `repo`, so a path that escaped that tree would land in scratch too.
        saved_tempdir, tempfile.tempdir = tempfile.tempdir, tmp
        try:
            for title, named in [
                    ("control: real work, deletions included", work),
                    (f"the same plus {typo!r}, which is nowhere", work + [typo]),
                    ("lesson/, by an absolute path through a symlink", [by_abs]),
                    ("the same work plus three paths not inside the repository",
                     work + not_inside)]:
                shutil.rmtree(seen, ignore_errors=True)
                code, out = None, io.StringIO()
                try:
                    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                        code = mine_tree(named, repo=repo)
                except Exception as exc:  # reported beside the other runs, not instead of them
                    print(f"raised {type(exc).__name__}: {exc}", file=out)
                runs.append((code, seen.exists(), out.getvalue(),
                             holds(seen / "lesson" / "draft.txt", "MY DRAFT\n")))
                print(f"  {title} ({'raised' if code is None else f'exit {code}'}):")
                for line in out.getvalue().rstrip().split("\n"):
                    print(f"      {line}".rstrip())
                print()
        finally:
            tempfile.tempdir = saved_tempdir
        (c_code, c_ran, _, _), (t_code, t_ran, t_out, _), \
            (a_code, _, _, a_saw), (o_code, o_ran, o_out, _) = runs
        refused = [ln.split("REFUSED", 1)[1].strip().rsplit("  (", 1)[0]
                   for ln in o_out.splitlines() if "REFUSED" in ln]
        checks += [
            ("the control ran its gate", c_ran),
            ("the control exits 0", c_code == 0),
            (f"{typo!r} is refused with exit 2", t_code == 2),
            (f"no gate ran for {typo!r}", not t_ran),
            (f"the refusal names {typo!r}", typo in t_out),
            ("lesson/ by absolute path is gated, exit 0", a_code == 0),
            ("its gate saw the untracked draft", a_saw),
            ("paths not inside the repository are refused with exit 2", o_code == 2),
            ("no gate ran for them", not o_ran),
            ("the refusal names exactly those three", refused == not_inside),
            ("lesson/ still holds my uncommitted work",
             holds(repo / "lesson" / "draft.txt", "MY DRAFT\n")
             and holds(repo / "lesson" / "keep.txt", "MY EDIT\n")),
            ("the directory beside the repository is untouched",
             holds(elsewhere / "precious.txt", "NOT IN THE REPO\n")),
        ]
    bad = [n for n, ok in checks if not ok]
    for name, ok in checks:
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
    print()
    if bad:
        print(f"SELFTEST FAILED: {', '.join(bad)}")
        return 1
    print("selftest passed: --mine gates your work and not a colleague's, by an absolute "
          "path too, and refuses a path that is nowhere or not inside the repository.")
    return 0


# An executable nothing installs, so the skip half of --selftest has a gate
# that cannot run. Checked before use: were it ever on PATH, the skip case
# would quietly become a second pass case, so the selftest refuses instead.
NO_SUCH_TOOL = "check-all-selftest-no-such-tool"


def selftest_skip() -> int:
    """Prove a gate that never RAN is not reported as a pass.

    The defect this replaced, found 2026-09-10: a gate whose executable was
    missing printed SKIP, was counted nowhere, and the run still ended `all 11
    gates pass.` with exit 0. So the runner is driven three times through the
    same GATES swap the failure half uses -- one real gate plus one whose
    executable does not exist, plain and then with --allow-skip -- and first a
    CONTROL of two real gates. The control is the run that must say `all 2
    gates`; that is what makes the phrase's absence from the other two a
    finding rather than a typo in the expected string.
    """
    global GATES
    if shutil.which(NO_SUCH_TOOL) is not None:
        print(f"SELFTEST FAILED: {NO_SUCH_TOOL} is on PATH, so a missing tool cannot be staged.")
        return 1
    real = [sys.executable, "-c", "pass"]
    cases = [
        ("control: two real gates", [("real", real), ("also real", real)], False),
        ("one gate's tool missing", [("real", real), ("missing tool", [NO_SUCH_TOOL])], False),
        ("the same, with --allow-skip", [("real", real), ("missing tool", [NO_SUCH_TOOL])], True),
    ]
    print("selftest: a gate whose executable does not exist\n")
    results = []
    for title, gates, allow in cases:
        GATES = gates
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = run_gates(REPO, "the working tree", allow_skip=allow)
        results.append((code, out.getvalue()))
        print(f"  {title} (exit {code}):")
        for line in out.getvalue().rstrip().split("\n"):
            print(f"      {line}".rstrip())
        print()
    (c_code, c_out), (s_code, s_out), (a_code, a_out) = results
    claim = "all 2 gates"
    checks = [
        ("the control exits 0", c_code == 0),
        (f"the control says '{claim}'", claim in c_out),
        ("a skip exits non-zero", s_code != 0),
        (f"a skip does not say '{claim}'", claim not in s_out),
        ("a skip says '1 of 2 gates ran'", "1 of 2 gates ran" in s_out),
        ("the skipped gate is named in the summary", "skipped: missing tool" in s_out),
        ("--allow-skip exits 0", a_code == 0),
        (f"--allow-skip still does not say '{claim}'", claim not in a_out),
        ("--allow-skip still names the skipped gate", "skipped: missing tool" in a_out),
    ]
    bad = [n for n, ok in checks if not ok]
    for name, ok in checks:
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
    print()
    if bad:
        print(f"SELFTEST FAILED: {', '.join(bad)}")
        return 1
    print("selftest passed: a gate that never ran was not reported as a pass.\n")
    return 0


def selftest() -> int:
    """A gate that failed, or never ran, must not be reported as passing.

    Proves this script still bites.
    """
    global GATES
    GATES = [("deliberate failure", [sys.executable, "-c", "raise SystemExit(3)"])]
    print("selftest: running one gate that exits 3\n")
    if run_gates(REPO, "the working tree") == 0:
        print("SELFTEST FAILED: a failing gate was reported as passing.")
        return 1
    print("selftest passed: the failure was reported.\n")
    if selftest_skip() != 0:
        return 1
    return selftest_mine()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--committed", action="store_true", help="run against git archive HEAD")
    parser.add_argument("--staged", action="store_true",
                        help="run against the tree your next commit would produce")
    parser.add_argument("--mine", nargs="+", metavar="PATH",
                        help="gate HEAD plus ONLY these paths of yours (uncommitted work)")
    parser.add_argument("--selftest", action="store_true",
                        help="prove a failure, or a skip, is reported")
    parser.add_argument("--allow-skip", action="store_true",
                        help="exit 0 even if a gate could not run (the summary still counts it)")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if args.mine:
        return mine_tree(args.mine, args.allow_skip)
    if args.committed:
        return committed_tree(args.allow_skip)
    if args.staged:
        return staged_tree(args.allow_skip)
    return run_gates(REPO, "the working tree", args.allow_skip)


if __name__ == "__main__":
    sys.exit(main())
