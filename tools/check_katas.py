#!/usr/bin/env python3
"""A folded answer must be folded correctly, and must have been run.

`## Practice` holds a kata: predict, run, check. Its answer is folded away in a
`<details>` block, and that block has two ways of being wrong that no other
gate here can see.

**The attribute.** `md_in_html` is enabled, so a `<details>` *without*
`markdown="1"` ships its body as literal Markdown -- asterisks and backticks
drawn on the published page. GitHub renders the same block correctly either
way and `mkdocs build --strict` passes, because a missing attribute is not a
broken link, so the author's own two previews are exactly the surfaces that
cannot show it. The library's first kata shipped like that on 2026-09-07 and
was found by reading the live site.

**The answer.** An answer typed by hand is a claim like any other, and this
library does not take claims on trust -- so a `## Practice` section has to
carry a generated block (`<!-- output: -->` or `<!-- source: -->`) inside the
fold. That is what makes the answer key run in CI on both platforms alongside
every other example: a solution cannot rot into one that no longer prints what
the page says it prints.

Nine checks, each one a rule from CONTRIBUTING's "Try it, and Practice":

1. Every `<details>` carries `markdown="1"`.
2. A `## Practice` section folds its answer in a `<details>`.
3. That fold contains at least one generated block.
4. `## Try it` comes before `## Practice`, which comes before `## See also`.
5. A stub has no `## Practice` -- there is no example behind it to answer with.
6. No `???` fold. It is Material-only and prints as literal text on GitHub,
   which is the mirror of defect 1.
7. Every `## Practice` has a row in KATAS.md. The index is the one file no
   lesson owns, so nothing about your page reveals that its row is missing.
8. Every row's two links resolve, and the kata link ends in `#practice`.
9. The IDs read K1, K2, K3... in table order, so the number is a label the
   table can renumber and never an address anyone saved.

    python3 tools/check_katas.py
    python3 tools/check_katas.py --selftest   # mutate each rule in turn

Code is stripped before any of this -- fenced blocks and inline spans both --
so a page may *show* a malformed block as an example, or name `<details>` in a
sentence, without failing its own gate. CONTRIBUTING does both.
"""

from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "site", ".venv", "__pycache__", ".github"}

FENCE = re.compile(r"^(```|~~~)", re.M)
CODE_SPAN = re.compile(r"`+[^`\n]*`+")
DETAILS = re.compile(r"<details\b[^>]*>", re.I)
GENERATED = re.compile(r"<!--\s*(output|source):")
STUB = re.compile(r"^> \*\*Stub", re.M)
KATAS = REPO / "KATAS.md"
ROW = re.compile(r"^\|\s*K(\d+)\s*\|\s*\[[^\]]*\]\(([^)]+)\)\s*\|\s*\[[^\]]*\]\(([^)]+)\)\s*\|", re.M)
ADMONITION_FOLD = re.compile(r"^\?\?\?", re.M)


def strip_code(text: str) -> str:
    """Blank out code, keeping line numbers intact.

    A page is allowed to *show* a wrong `<details>` as an example, and to name
    the tag inside backticks in a sentence. Only markup the page actually
    emits is the page's own, so only that is checked. Both forms are removed:
    fenced blocks, and inline spans -- the second one is not an edge case, it
    is how this gate's own rules are written down in CONTRIBUTING.
    """
    out, in_fence = [], False
    for line in text.split("\n"):
        if FENCE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else CODE_SPAN.sub("", line))
    return "\n".join(out)


def section(text: str, heading: str) -> str | None:
    """The body under `## <heading>`, up to the next `## `, or None."""
    m = re.search(rf"^## {re.escape(heading)}\s*$", text, re.M)
    if not m:
        return None
    rest = text[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def pages() -> list[pathlib.Path]:
    found = []
    for p in sorted(REPO.rglob("*.md")):
        if any(part in SKIP_DIRS for part in p.relative_to(REPO).parts):
            continue
        found.append(p)
    return found


def check_text(rel: str, raw: str) -> list[str]:
    """Every defect in one page's markup, as finished sentences."""
    text = strip_code(raw)
    bad: list[str] = []

    for tag in DETAILS.findall(text):
        if 'markdown="1"' not in tag and "markdown='1'" not in tag:
            bad.append(
                f"{rel}: `{tag}` has no markdown=\"1\", so md_in_html leaves its "
                "body as literal Markdown on the site. GitHub and --strict will "
                "both stay green."
            )

    if ADMONITION_FOLD.search(text):
        bad.append(
            f"{rel}: a `???` collapsible is Material-only and prints as literal "
            'text on GitHub. Use <details markdown="1">.'
        )

    practice = section(text, "Practice")
    if practice is None:
        return bad

    if STUB.search(text):
        bad.append(
            f"{rel}: a stub has a `## Practice` section. There is no example "
            "behind the page, so the answer cannot have been run."
        )

    if not DETAILS.search(practice):
        bad.append(
            f"{rel}: `## Practice` does not fold its answer in a <details> "
            "block, so the kata is spoiled by the page that sets it."
        )
    elif not GENERATED.search(practice):
        bad.append(
            f"{rel}: `## Practice` folds an answer that was typed, not run. Put "
            "the solution in examples/<stem>_kata_sh.sh and paste it with "
            "<!-- output:<stem>_kata_sh -->, so CI checks the answer too."
        )

    # Compare DOCUMENT order against the canonical one. Building the list by
    # iterating the canonical tuple would produce it sorted by construction --
    # a check that cannot fail, which is what the selftest caught.
    seen = []
    for h in ("Try it", "Practice", "See also"):
        m = re.search(rf"^## {re.escape(h)}\s*$", text, re.M)
        if m:
            seen.append((m.start(), h))
    seen.sort()
    names = [h for _, h in seen]
    canonical = [h for h in ("Try it", "Practice", "See also") if h in names]
    if names != canonical:
        bad.append(
            f"{rel}: the closing sections are in the order {names}. "
            "CONTRIBUTING puts them Try it, then Practice, then See also."
        )
    return bad


def index_rows() -> list[tuple[int, str, str]]:
    """(number, kata href, lesson href) for every row of the KATAS.md table."""
    if not KATAS.exists():
        return []
    return [(int(n), k, l) for n, k, l in ROW.findall(KATAS.read_text(encoding="utf-8"))]


def check_index(practice_pages: set[str]) -> list[str]:
    """The index and the pages must agree, and the numbering must be a sequence."""
    bad: list[str] = []
    if not KATAS.exists():
        return [f"KATAS.md is missing, and {len(practice_pages)} page(s) have a kata."]

    rows = index_rows()
    numbers = [n for n, _, _ in rows]
    if numbers != list(range(1, len(numbers) + 1)):
        bad.append(
            f"KATAS.md numbers its rows {numbers} -- they must read K1, K2, K3... "
            "in table order. The number is a label the table renumbers freely; "
            "that only works while it matches the position."
        )

    indexed: set[str] = set()
    for n, kata_href, lesson_href in rows:
        if not kata_href.endswith("#practice"):
            bad.append(f"KATAS.md K{n}: the kata link is {kata_href!r}, which does "
                       "not end in #practice, so it lands on the page rather than "
                       "on the exercise.")
        for href in (kata_href, lesson_href):
            target = REPO / href.split("#", 1)[0]
            if not target.exists():
                bad.append(f"KATAS.md K{n}: {href!r} names no such file.")
        indexed.add(kata_href.split("#", 1)[0])

    for rel in sorted(practice_pages - indexed):
        bad.append(
            f"{rel}: has a `## Practice` section and no row in KATAS.md. Nothing "
            "on the page can reveal that -- add the row where the kata should be "
            "attempted, and renumber."
        )
    for rel in sorted(indexed - practice_pages):
        bad.append(f"KATAS.md points at {rel}, which has no `## Practice` section.")
    return bad


def scan() -> list[str]:
    bad: list[str] = []
    practice: set[str] = set()
    for p in pages():
        rel = str(p.relative_to(REPO))
        raw = p.read_text(encoding="utf-8")
        bad += check_text(rel, raw)
        if rel != "KATAS.md" and section(strip_code(raw), "Practice") is not None:
            practice.add(rel)
    return bad + check_index(practice)


GOOD = """# A page

## Try it

1. Do a thing.

## Practice

Predict it.

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:a_kata_sh -->
```text
the answer
```
<!-- /output -->

</details>

## See also

- Something
"""

MUTATIONS = [
    ("a <details> with no markdown=\"1\"",
     lambda t: t.replace('<details markdown="1">', "<details>")),
    ("a ??? fold instead of <details>",
     lambda t: t.replace('<details markdown="1">', "??? note")),
    ("an answer that was typed, not run",
     lambda t: t.replace("<!-- output:a_kata_sh -->", "").replace("<!-- /output -->", "")),
    ("an unfolded answer",
     lambda t: t.replace('<details markdown="1">', "").replace("</details>", "")),
    ("Practice before Try it",
     lambda t: t.replace("## Try it", "## TRY IT LATER").replace("## See also", "## Try it\n\n## See also")),
    ("a stub carrying a Practice section",
     lambda t: t.replace("# A page", "# A page\n\n> **Stub — an outline, not a lesson.**")),
]


def selftest() -> int:
    print("selftest: one good page, then one mutation at a time\n")
    failures = 0

    clean = check_text("fixture.md", GOOD)
    ok = not clean
    failures += 0 if ok else 1
    print(f"  {'ok  ' if ok else 'FAIL'}  the good page passes")
    for line in clean:
        print(f"          unexpected: {line}")

    # The rules are written down in prose that names the tag. A gate that
    # fails the file describing it is not a gate, it is a trap.
    prose = GOOD + "\nA page may write `<details>` and `???` in a sentence.\n"
    ok = not check_text("fixture.md", prose)
    failures += 0 if ok else 1
    print(f"  {'ok  ' if ok else 'FAIL'}  a <details> named in an inline code span is ignored")

    for name, mutate in MUTATIONS:
        caught = bool(check_text("fixture.md", mutate(GOOD)))
        failures += 0 if caught else 1
        print(f"  {'ok  ' if caught else 'FAIL'}  {name}")
        if not caught:
            print("          expected a complaint, GOT NONE")

    # The index rules read KATAS.md, so they are exercised against a temporary
    # one -- same trick as check_nav_chain's selftest, which swaps NAV_ORDER out
    # rather than editing the repo to prove a gate bites.
    global KATAS
    saved = KATAS
    import tempfile
    good_row = ("| # | Kata | Lesson | Level |\n|---|---|---|---|\n"
                "| K1 | [k](CONTRIBUTING.md#practice) | [l](CONTRIBUTING.md) | 101 |\n")
    index_cases = [
        ("a kata with no row in the index", good_row, {"CONTRIBUTING.md", "orphan.md"}),
        ("a row pointing at a page with no kata", good_row, set()),
        ("numbering that skips",
         good_row.replace("| K1 |", "| K2 |"), {"CONTRIBUTING.md"}),
        ("a kata link that does not reach #practice",
         good_row.replace("#practice", ""), {"CONTRIBUTING.md"}),
        ("a row naming a file that does not exist",
         good_row.replace("CONTRIBUTING.md#practice", "NOPE.md#practice"), {"CONTRIBUTING.md"}),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        for name, body, practice in index_cases:
            KATAS = pathlib.Path(tmp) / "KATAS.md"
            KATAS.write_text(body, encoding="utf-8")
            caught = bool(check_index(practice))
            failures += 0 if caught else 1
            print(f"  {'ok  ' if caught else 'FAIL'}  {name}")
            if not caught:
                print("          expected a complaint, GOT NONE")
        # and the good one must stay quiet
        KATAS = pathlib.Path(tmp) / "KATAS.md"
        KATAS.write_text(good_row, encoding="utf-8")
        quiet = not check_index({"CONTRIBUTING.md"})
        failures += 0 if quiet else 1
        print(f"  {'ok  ' if quiet else 'FAIL'}  a correct index says nothing")
    KATAS = saved

    print()
    if failures:
        print(f"selftest FAILED: {failures} case(s) wrong. A check that survives "
              "its own mutation is not guarding anything.")
        return 1
    print(f"selftest ok: {len(MUTATIONS)} page mutations and {len(index_cases)} "
          "index mutations, each one reported.")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    bad = scan()
    if not bad:
        n = len(index_rows())
        print(f"katas: K1-K{n}, each folded correctly, answered by a program, "
              "and indexed.")
        return 0
    print("katas: folded answers that will not render, or were not run.\n")
    for line in bad:
        print(f"  {line}")
    print("\n  CONTRIBUTING.md, 'Try it, and Practice', has the rules and why.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
