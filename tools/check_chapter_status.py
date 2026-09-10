#!/usr/bin/env python3
"""A row per page stays true; a count of pages goes stale.

Three files say which lessons exist and which are still stubs, in three
different shapes, and none of them is owned by the lesson it describes:

* every chapter `README.md` has a `| # | Lesson | ... | Status |` table,
* `ROADMAP.md` has one status row per page for the whole library,
* `00_Start_Here/README.md` has a chapter map whose last column is a
  **count** -- `7 / 0` -- of pages that live somewhere else.

Measured on 2026-09-07, the shape decided the outcome. Every surface with one
row per page was correct: 14 chapter tables, 76 ROADMAP rows, all of KATAS.md.
Every surface that aggregated had drifted. All eight cells of the chapter map
were wrong at once -- `3 / 0` for a chapter with seven written lessons, `5 / 1`
against an actual `11 / 2` -- because a count is the one claim that goes false
when you touch a *different* file. ROADMAP had the same disease in its own
dialect: four rows reading *"the other three pages | stubs"*, two of which were
four pages, one of which swept a **written** lesson (`terminal_hyperlinks`) in
among the stubs, and three written lessons (`the_nul_byte`, `pcre2`,
`decompress_then_decode`) that no row mentioned at all.

That is why this gate exists rather than a build-time hook in
`mkdocs_hooks.py`. A hook fixes the published site and leaves GitHub -- which
this library is read on, and which CONTRIBUTING already writes rules for --
showing the stale number. The house pattern for a shared index is a gate:
`check_katas.py` rule 7 says every kata needs a row in KATAS.md, "the one file
no lesson owns, so nothing about your page reveals that its row is missing."
The chapter map is that file for chapters.

Seven checks:

1. **Every chapter has a map row, and every map row names a chapter.** The map
   listed 01-08 for a library of fourteen; six chapters had no row and nothing
   said so.
2. **Each row's `Written / stub` equals the tree.** `--fix` writes these; they
   are arithmetic and nobody should be typing them.
3. **Every lesson has a row in its chapter's table**, and no row names a folder
   that is gone.
4. **A lesson row's Status agrees with the page** -- a stub says stub, a
   written page does not.
5. **Every lesson has a ROADMAP row.**
6. **That row's status agrees with the page too.**
7. **A chapter's lesson table lists its lessons in `NAV_ORDER`'s order.**

Checks 3-6 are what make check 2 safe to generate. A count computed from the
tree can never disagree with the tree, so on its own it would be true and
uninformative; it is worth reading only because the per-page rows it summarises
are themselves checked against the same tree.

Check 7 is the one whose authority is not the tree. A folder name is a
permanent URL, so nothing on disk says what order the lessons are read in --
`NAV_ORDER` in `mkdocs_hooks.py` does, and the sidebar and the footer arrows
are two renderings of it that `check_nav_chain.py` holds together. The chapter
table is a third, and the only one with numbers on it: a reader who sees row
13 expects the thirteenth page in the sidebar. On 2026-09-08 two new
02_Characters rows sat after `logical_and_visual_order` while NAV_ORDER put
them straight after `a_code_point_is_not_a_character`, and all eleven gates in
`check_all.py` passed -- checks 3 and 4 ask whether a row exists and what it
says, never where it is. It was caught by eye.

Which table is the lesson table is decided by its header, `| # | ... | Status |`,
and never by a row that starts with a number. A chapter README can hold more
than one numbered table: 11_Tools opens with a question table whose rows link
`grep/README.md`, and 13_Documentation has one linking
`a_page_has_a_date/README.md`, both in an order that is not reading order.
Checks 3 and 4 read the same table through the same function. Until 2026-09-10
they read every table on the page and kept the first link to each lesson, so
five 11_Tools lessons -- grep, ripgrep, pcre2, find and sh -- took their status
from the question table, which has no Status column, and check 4 skipped them
without a word. Their Status cells happened to be right.

    python3 tools/check_chapter_status.py
    python3 tools/check_chapter_status.py --fix       # rewrite the count cells
    python3 tools/check_chapter_status.py --selftest  # mutate each check in turn

Stdlib only, and every function takes a root -- NAV_ORDER included, which is
parsed out of that root's `mkdocs_hooks.py` rather than imported -- so this runs
unchanged inside the temporary tree `check_all.py --committed` and `--mine`
extract, and in examples.yml, which installs no docs group.
"""

from __future__ import annotations

import ast
import difflib
import pathlib
import re
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent

# The map is a chapter directory too, and it is the one page that describes the
# others rather than holding lessons -- so it is named, not inferred.
MAP_DIR = "00_Start_Here"
MAP_PAGE = f"{MAP_DIR}/README.md"
ROADMAP = "ROADMAP.md"
# Where NAV_ORDER lives. Parsed, never imported -- see nav_order().
HOOKS = "mkdocs_hooks.py"

CHAPTER = re.compile(r"^\d\d_")
STUB_NOTICE = re.compile(r"^> \*\*Stub", re.M)
COUNT_HEADER = "Written / stub"
STATUS_HEADER = "Status"
NUMBER_HEADER = "#"
COUNT_CELL = re.compile(r"^\s*(\d+)\s*/\s*(\d+)\s*$")
LINK = re.compile(r"\]\(([^)]+)\)")
LESSON_HREF = re.compile(r"([a-z0-9_]+)/README\.md")


# --------------------------------------------------------------------------
# the tree, which decides what exists and what is a stub -- not the order
# --------------------------------------------------------------------------

def measure(root: pathlib.Path) -> dict[str, dict[str, bool]]:
    """`{chapter: {lesson: is_stub}}`, read off disk.

    A lesson is a folder with a `README.md`; it is a stub when that page
    carries the `> **Stub` notice CONTRIBUTING requires. That is the same
    test a reader applies, which is the point -- the notice is the claim, so
    the notice is what is counted.
    """
    tree: dict[str, dict[str, bool]] = {}
    for chapter in sorted(root.iterdir()):
        if not chapter.is_dir() or not CHAPTER.match(chapter.name):
            continue
        if chapter.name == MAP_DIR:
            continue
        lessons = {}
        for folder in sorted(chapter.iterdir()):
            page = folder / "README.md"
            if folder.is_dir() and page.is_file():
                text = page.read_text(encoding="utf-8")
                lessons[folder.name] = bool(STUB_NOTICE.search(text))
        tree[chapter.name] = lessons
    return tree


# --------------------------------------------------------------------------
# table parsing
# --------------------------------------------------------------------------

def cells(line: str) -> list[str]:
    """The cells of a pipe-table row, outer pipes dropped."""
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_divider(line: str) -> bool:
    stripped = line.strip()
    return (stripped.startswith("|")
            and set(stripped) <= set("|-: ")
            and "-" in stripped)


def tables(text: str) -> list[tuple[list[str], list[tuple[int, list[str]]]]]:
    """Every pipe table as `(header cells, [(line number, row cells)])`.

    Line numbers are 0-based indices into `text.splitlines()`, so `--fix` can
    put a rewritten row back exactly where it came from.
    """
    lines = text.splitlines()
    found = []
    i = 0
    while i < len(lines) - 1:
        if lines[i].lstrip().startswith("|") and is_divider(lines[i + 1]):
            header = cells(lines[i])
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append((j, cells(lines[j])))
                j += 1
            found.append((header, rows))
            i = j
        else:
            i += 1
    return found


def column(header: list[str], name: str) -> int | None:
    """Index of the column headed `name`, or None. Never a fixed position.

    14_Resources' table has neither a `#` nor a `Status` column, on purpose --
    it is a resources chapter, not a chapter of the course. Locating a column
    by its heading lets that page keep its own shape instead of being made
    uniform to suit a regex.
    """
    for i, cell in enumerate(header):
        if cell == name:
            return i
    return None


def links(cell: str) -> list[str]:
    return LINK.findall(cell)


def is_lesson_table(header: list[str]) -> bool:
    """Whether a table is a chapter's lesson table: `| # | ... | Status |`.

    Decided by the header, never by a row that starts with a number. A chapter
    README can hold more than one numbered table -- 11_Tools opens with a
    question table whose rows are numbered 1, 2, 3, 3b and link grep/README.md
    -- and a scan of every `| N |` row takes that one for reading order too.
    The middle headings vary (`Lesson`, `Page`), so they are not the test.
    """
    return (column(header, NUMBER_HEADER) is not None
            and column(header, STATUS_HEADER) is not None)


def lesson_tables(text: str
                  ) -> list[tuple[list[str], list[tuple[int, list[str]]]]]:
    """The lesson tables on a chapter page, in page order. Normally one."""
    return [(header, rows) for header, rows in tables(text)
            if is_lesson_table(header)]


def subject(row: list[str]) -> str | None:
    """The lesson folder a row is about: the first one it links, left to right.

    That is the Lesson (or Page) cell rather than a neighbour the question
    cell happens to mention -- the rule ROADMAP rows follow, for that reason.
    """
    for cell in row:
        for href in links(cell):
            match = LESSON_HREF.fullmatch(href)
            if match:
                return match.group(1)
    return None


# --------------------------------------------------------------------------
# checks 1-6: membership and status, measured against the tree
# --------------------------------------------------------------------------

def map_rows(text: str) -> list[tuple[int, str, list[str], int]]:
    """Chapter-map rows: `(line, chapter, cells, count column)`.

    A row qualifies by naming `../<chapter>/README.md` in its first cell, so
    the map may be split into as many tables as the page wants -- today the
    reading spine and the chapters you can take any time -- without this
    parser knowing or caring.
    """
    out = []
    for header, rows in tables(text):
        col = column(header, COUNT_HEADER)
        if col is None:
            continue
        for line, row in rows:
            if not row:
                continue
            for href in links(row[0]):
                match = re.fullmatch(r"\.\./(\d\d_[A-Za-z_]+)/README\.md", href)
                if match:
                    out.append((line, match.group(1), row, col))
                    break
    return out


def check_map(root: pathlib.Path, tree: dict[str, dict[str, bool]]
              ) -> list[tuple[str, str]]:
    page = root / MAP_PAGE
    if not page.is_file():
        return [("map-rows", f"{MAP_PAGE} is missing -- it is the chapter map")]

    rows = map_rows(page.read_text(encoding="utf-8"))
    listed = {chapter: (row, col) for _line, chapter, row, col in rows}
    problems = []

    for chapter in tree:
        if chapter not in listed:
            problems.append((
                "map-rows",
                f"{MAP_PAGE} has no row for {chapter}/ -- a reader who lands "
                f"on the map cannot see that chapter exists"))
    for chapter in listed:
        if chapter not in tree:
            problems.append((
                "map-rows",
                f"{MAP_PAGE} has a row for {chapter}/, which is not a chapter "
                f"with lessons in it"))

    for chapter, (row, col) in sorted(listed.items()):
        if chapter not in tree:
            continue
        if col >= len(row):
            problems.append((
                "map-counts",
                f"{chapter}: the row has no {COUNT_HEADER!r} cell"))
            continue
        want = counts(tree[chapter])
        match = COUNT_CELL.match(row[col])
        if not match:
            problems.append((
                "map-counts",
                f"{chapter}: {row[col]!r} is not a count -- expected "
                f"{want[0]} / {want[1]}"))
        elif (int(match.group(1)), int(match.group(2))) != want:
            problems.append((
                "map-counts",
                f"{chapter}: the map says {row[col]}, the tree says "
                f"{want[0]} / {want[1]}"))
    return problems


def counts(lessons: dict[str, bool]) -> tuple[int, int]:
    return (sum(1 for stub in lessons.values() if not stub),
            sum(1 for stub in lessons.values() if stub))


def says_stub(status: str) -> bool:
    return status.strip().lower().startswith("stub")


def check_chapters(root: pathlib.Path, tree: dict[str, dict[str, bool]]
                   ) -> list[tuple[str, str]]:
    problems = []
    for chapter, lessons in tree.items():
        page = root / chapter / "README.md"
        if not page.is_file():
            problems.append((
                "chapter-rows", f"{chapter}/README.md is missing"))
            continue
        text = page.read_text(encoding="utf-8")

        rowed: dict[str, tuple[str | None, int]] = {}
        # The lesson table -- the one check 7 reads, through the same
        # function. A page without one is read table by table instead, which
        # is 14_Resources on purpose: its table has no `#` or Status column.
        for header, rows in lesson_tables(text) or tables(text):
            status_col = column(header, STATUS_HEADER)
            for line, row in rows:
                lesson = subject(row)
                if lesson is None:
                    continue
                status = (row[status_col]
                          if status_col is not None
                          and status_col < len(row) else None)
                rowed.setdefault(lesson, (status, line))

        for lesson in lessons:
            if lesson not in rowed:
                problems.append((
                    "chapter-rows",
                    f"{chapter}/README.md has no table row for {lesson}/ -- "
                    f"the chapter's own front door does not list the lesson"))
        for lesson in rowed:
            if lesson not in lessons:
                problems.append((
                    "chapter-rows",
                    f"{chapter}/README.md has a row for {lesson}/, which is "
                    f"not a lesson folder"))

        for lesson, (status, line) in sorted(rowed.items()):
            if lesson not in lessons or status is None:
                continue
            if says_stub(status) != lessons[lesson]:
                real = "a stub" if lessons[lesson] else "written"
                problems.append((
                    "chapter-status",
                    f"{chapter}/README.md:{line + 1} calls {lesson}/ "
                    f"{status!r}; the page is {real}"))
    return problems


def check_roadmap(root: pathlib.Path, tree: dict[str, dict[str, bool]]
                  ) -> list[tuple[str, str]]:
    page = root / ROADMAP
    if not page.is_file():
        return [("roadmap-missing", f"{ROADMAP} is missing")]

    rowed: dict[str, tuple[str, int]] = {}
    for _header, rows in tables(page.read_text(encoding="utf-8")):
        for line, row in rows:
            if len(row) < 2:
                continue
            # A row's status describes the page its FIRST cell links. The
            # status cell links things for its own reasons -- an RFC, a
            # neighbouring page -- and reading those as subjects is how the
            # aggregate rows came to call a written lesson a stub.
            for href in links(row[0]):
                match = re.fullmatch(r"(\d\d_[A-Za-z_]+)/([a-z0-9_]+)/README\.md",
                                     href)
                if match:
                    rowed.setdefault(href, (row[1], line))

    problems = []
    for chapter, lessons in tree.items():
        for lesson, stub in lessons.items():
            href = f"{chapter}/{lesson}/README.md"
            if href not in rowed:
                problems.append((
                    "roadmap-missing",
                    f"{ROADMAP} has no row for {href} -- the roadmap is the "
                    f"library's status page and this page is not on it"))
                continue
            status, line = rowed[href]
            if says_stub(status) != stub:
                real = "a stub" if stub else "written"
                problems.append((
                    "roadmap-status",
                    f"{ROADMAP}:{line + 1} calls {href} {status[:40]!r}; the "
                    f"page is {real}"))
    for href in rowed:
        chapter, lesson, _ = href.split("/")
        if chapter in tree and lesson not in tree[chapter]:
            problems.append((
                "roadmap-missing",
                f"{ROADMAP} has a row for {href}, which no longer exists"))
    return problems


# --------------------------------------------------------------------------
# check 7: order, measured against NAV_ORDER -- the tree has no order
# --------------------------------------------------------------------------

def nav_order(root: pathlib.Path) -> dict[str, list[str]]:
    """`NAV_ORDER` out of `root/mkdocs_hooks.py`, parsed with `ast`.

    Parsed rather than imported, so the gate stays stdlib-only -- examples.yml
    runs it with no docs group -- and keyed to `root` like everything else
    here, which is what lets the selftest's miniature library carry an order
    of its own. The hook writes an annotated assignment; a plain one reads the
    same, and the last module-level binding wins, as it would on import.

    Raises ValueError, with a sentence to act on, when there is no order to
    read. A gate that cannot find what it compares against has to say so;
    passing would be the silent no-op this file exists to replace.
    """
    path = root / HOOKS
    if not path.is_file():
        raise ValueError(f"{HOOKS} is missing, so there is no NAV_ORDER to "
                         f"hold the lesson tables to")
    try:
        module = ast.parse(path.read_text(encoding="utf-8"), filename=HOOKS)
    except SyntaxError as err:
        raise ValueError(f"{HOOKS} does not parse: {err.msg} "
                         f"(line {err.lineno})") from None
    value = None
    for node in module.body:
        if isinstance(node, ast.AnnAssign):
            targets = [node.target]
        elif isinstance(node, ast.Assign):
            targets = node.targets
        else:
            continue
        if node.value is not None and any(
                isinstance(target, ast.Name) and target.id == "NAV_ORDER"
                for target in targets):
            value = node.value
    if value is None:
        raise ValueError(f"{HOOKS} has no module-level NAV_ORDER to read")
    try:
        order = ast.literal_eval(value)
    except (ValueError, TypeError):
        raise ValueError(f"NAV_ORDER in {HOOKS} is not a literal, and this "
                         f"gate reads it rather than running the hook") from None
    if not isinstance(order, dict):
        raise ValueError(f"NAV_ORDER in {HOOKS} is a {type(order).__name__}, "
                         f"not a dict")
    return order


def sidebar_order(listed: list[str], folders: list[str]) -> list[str]:
    """`folders` in the order the sidebar shows them, given NAV_ORDER's list.

    Listed names first, in the listed order, then the unlisted ones
    alphabetically -- CONTRIBUTING's "unlisted pages sort alphabetically at the
    bottom", which `_order_key` in the hook implements. Restated rather than
    imported, for the reason NAV_ORDER is parsed.
    """
    rank: dict[str, int] = {}
    for i, name in enumerate(listed):
        rank.setdefault(name, i)

    def key(name: str) -> tuple[int, str]:
        if name in rank:
            return (rank[name], "")
        return (len(listed), name.lower())

    return sorted(folders, key=key)


def check_order(root: pathlib.Path, tree: dict[str, dict[str, bool]]
                ) -> list[tuple[str, str]]:
    """Check 7: each lesson table lists its lessons in the sidebar's order.

    The reference is NAV_ORDER restricted to the folders the table lists. A
    lesson missing from the table, or a row naming a folder that is not a
    lesson, is check 3's to report, so both are left out here rather than
    reported twice. A lesson the table lists and NAV_ORDER does not is placed
    where the sidebar really puts it, at the alphabetical tail -- so a row
    numbered 2 for a page the sidebar shows last is caught, which is the
    defect whichever of the two is wrong.
    """
    try:
        order = nav_order(root)
    except ValueError as err:
        return [("chapter-order", str(err))]

    problems = []
    for chapter, lessons in tree.items():
        page = root / chapter / "README.md"
        if not page.is_file():
            continue                                  # check 3 said so
        text = page.read_text(encoding="utf-8")
        rows = []
        for _header, table_rows in lesson_tables(text):
            for line, row in table_rows:
                lesson = subject(row)
                if lesson in lessons:
                    rows.append((line, lesson))
        # A page with no lesson table (14_Resources) has no numbers to hold.
        table = [lesson for _line, lesson in rows]
        listed = order.get(chapter, [])
        sidebar = sidebar_order(listed, table)
        if table == sidebar:
            continue

        at = next(i for i, (a, b) in enumerate(zip(table, sidebar)) if a != b)
        reference = f"NAV_ORDER[{chapter!r}]"
        unlisted = sorted((name for name in table if name not in listed),
                          key=str.lower)
        if chapter not in order:
            reference += " -- absent, so the sidebar sorts alphabetically"
        elif unlisted:
            reference += " then, alphabetically, " + ", ".join(unlisted)
        diff = difflib.unified_diff(
            sidebar, table, fromfile=reference,
            tofile=f"{chapter}/README.md, the lesson table",
            n=1, lineterm="")
        problems.append((
            "chapter-order",
            f"{chapter}/README.md:{rows[at][0] + 1}: the lesson table leaves "
            f"NAV_ORDER's order at position {at + 1} -- the table has "
            f"{table[at]} there, the sidebar has {sidebar[at]}:\n"
            + "\n".join(f"      {diff_line}" for diff_line in diff)))
    return problems


def problems(root: pathlib.Path) -> list[tuple[str, str]]:
    tree = measure(root)
    return (check_map(root, tree)
            + check_chapters(root, tree)
            + check_roadmap(root, tree)
            + check_order(root, tree))


# --------------------------------------------------------------------------
# --fix, for the one thing that is arithmetic
# --------------------------------------------------------------------------

def fix_counts(root: pathlib.Path) -> list[str]:
    """Rewrite the map's count cells from the tree. Returns what changed.

    Only the counts. Everything else this gate checks is prose -- a status
    word, a row that has to be written where a person decides it goes -- and a
    tool that invented those would be answering the question instead of
    asking it.
    """
    tree = measure(root)
    page = root / MAP_PAGE
    lines = page.read_text(encoding="utf-8").splitlines(keepends=True)
    plain = [line.rstrip("\n") for line in lines]
    changed = []
    for line, chapter, row, col in map_rows("".join(lines)):
        if chapter not in tree or col >= len(row):
            continue
        want = "%d / %d" % counts(tree[chapter])
        if row[col] == want:
            continue
        changed.append(f"{chapter}: {row[col] or '(empty)'} -> {want}")
        new = list(row)
        new[col] = want
        ending = "\n" if lines[line].endswith("\n") else ""
        plain[line] = "| " + " | ".join(new) + " |"
        lines[line] = plain[line] + ending
    if changed:
        page.write_text("".join(lines), encoding="utf-8")
    return changed


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------

GOOD_MAP = """\
# Start here

| Chapter | What it settles | Written / stub |
|---|---|---|
| [01_One](../01_One/README.md) | the first thing | 1 / 1 |

| Chapter | What it settles | Written / stub |
|---|---|---|
| [02_Two](../02_Two/README.md) | the second thing | 1 / 0 |
"""

GOOD_CHAPTERS = {
    # 01_One opens with a numbered question table, as 11_Tools and
    # 13_Documentation do, and its rows link the lessons in the WRONG order.
    # It is the decoy every check has to see past: it comes first and has no
    # Status column, so a parser reading every table would take Beta's status
    # from it -- and a scan of every `| N |` row would fail this good tree on
    # order. Unmutated, the tree has to pass anyway.
    "01_One": """\
# 01_One

| | The question | Why it bites |
|---|---|---|
| 1 | Where does it go wrong? | [Beta](beta/README.md), before [Alpha](alpha/README.md) |
| 2 | And after that? | [Alpha](alpha/README.md) |

| # | Lesson | The question it answers | Status |
|---|---|---|---|
| 1 | [Alpha](alpha/README.md) | why? | written |
| 2 | [Beta](beta/README.md) | how? | stub |
""",
    "02_Two": """\
# 02_Two

| | What it is |
|---|---|
| [Gamma](gamma/README.md) | a page with no Status column |
""",
}

GOOD_ROADMAP = """\
# Roadmap

| Page | Status |
|---|---|
| [Alpha](01_One/alpha/README.md) | written, 2026-09-07 |
| [Beta](01_One/beta/README.md) | stub |
| [Gamma](02_Two/gamma/README.md) | written, 2026-09-07 |
"""

# Written the way the real hook writes it, as an annotated assignment.
GOOD_HOOKS = """\
NAV_ORDER: dict[str, list[str]] = {
    "01_One": ["README.md", "alpha", "beta"],
    "02_Two": ["README.md", "gamma"],
}
"""

STUB_TEXT = ("# Beta\n\n**Level:** 101 · for anyone\n\n"
             "> **Stub — an outline, not a lesson.** No example behind it yet.\n")
PAGE_TEXT = "# A page\n\n**Level:** 101 · for anyone\n\nProse.\n"


def build(root: pathlib.Path) -> None:
    """A miniature library that passes every check."""
    (root / MAP_DIR).mkdir(parents=True)
    (root / MAP_PAGE).write_text(GOOD_MAP, encoding="utf-8")
    (root / ROADMAP).write_text(GOOD_ROADMAP, encoding="utf-8")
    (root / HOOKS).write_text(GOOD_HOOKS, encoding="utf-8")
    for chapter, text in GOOD_CHAPTERS.items():
        (root / chapter).mkdir()
        (root / chapter / "README.md").write_text(text, encoding="utf-8")
    for path, text in (("01_One/alpha", PAGE_TEXT),
                       ("01_One/beta", STUB_TEXT),
                       ("02_Two/gamma", PAGE_TEXT)):
        (root / path).mkdir()
        (root / path / "README.md").write_text(text, encoding="utf-8")


def edit(root: pathlib.Path, rel: str, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"selftest is stale: {old!r} not in {rel}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def drop_chapter_row(root: pathlib.Path) -> None:
    edit(root, "01_One/README.md",
         "| 2 | [Beta](beta/README.md) | how? | stub |\n", "")


def add_chapter(root: pathlib.Path) -> None:
    (root / "03_Three" / "delta").mkdir(parents=True)
    (root / "03_Three" / "delta" / "README.md").write_text(
        PAGE_TEXT, encoding="utf-8")
    (root / "03_Three" / "README.md").write_text(
        "# 03_Three\n\n| # | Lesson | The question it answers | Status |\n"
        "|---|---|---|---|\n| 1 | [Delta](delta/README.md) | eh? | written |\n",
        encoding="utf-8")
    edit(root, ROADMAP, "| [Gamma]",
         "| [Delta](03_Three/delta/README.md) | written, 2026-09-07 |\n| [Gamma]")


def swap_rows(root: pathlib.Path) -> None:
    """Alpha and Beta trade places and are renumbered, so the `#` column still
    reads 1, 2 and nothing on the page looks wrong -- the 2026-09-08 near-miss
    in miniature."""
    edit(root, "01_One/README.md",
         "| 1 | [Alpha](alpha/README.md) | why? | written |\n"
         "| 2 | [Beta](beta/README.md) | how? | stub |\n",
         "| 1 | [Beta](beta/README.md) | how? | stub |\n"
         "| 2 | [Alpha](alpha/README.md) | why? | written |\n")


def graduate(root: pathlib.Path) -> None:
    """Beta loses its stub notice -- the everyday event every count misses."""
    (root / "01_One/beta/README.md").write_text(PAGE_TEXT, encoding="utf-8")


MUTATIONS: list[tuple[str, object, set[str]]] = [
    ("the good tree, unmutated -- decoy question table and all",
     lambda root: None, set()),
    ("a chapter with no row on the map", add_chapter, {"map-rows"}),
    ("a map row for a chapter that is gone",
     lambda root: edit(root, MAP_PAGE, "[02_Two](../02_Two/README.md)",
                       "[02_Gone](../02_Gone/README.md)"),
     # Twice over: 02_Two has lost its row and 02_Gone has no chapter. Its
     # count is NOT checked -- there is no tree to check it against, and a
     # second complaint about a chapter that does not exist is noise.
     {"map-rows"}),
    ("a count that is one out",
     lambda root: edit(root, MAP_PAGE, "| 1 / 1 |", "| 3 / 0 |"),
     {"map-counts"}),
    ("a count cell that is not a count",
     lambda root: edit(root, MAP_PAGE, "| 1 / 1 |", "| several |"),
     {"map-counts"}),
    ("a lesson with no row in its chapter table", drop_chapter_row,
     {"chapter-rows"}),
    ("a chapter row naming a folder that is gone",
     lambda root: edit(root, "01_One/README.md",
                       "| [Beta](beta/README.md) | how? |",
                       "| [Beta](gone/README.md) | how? |"),
     {"chapter-rows"}),
    ("a Status column that calls a stub written",
     lambda root: edit(root, "01_One/README.md",
                       "| how? | stub |", "| how? | written |"),
     {"chapter-status"}),
    # Check 7. The unmutated tree already proves the decoy table is ignored;
    # these prove the lesson table is not.
    ("two lesson rows swapped and renumbered", swap_rows, {"chapter-order"}),
    ("a lesson NAV_ORDER does not list, so the sidebar files it last",
     lambda root: edit(root, HOOKS, '"alpha", "beta"', '"beta"'),
     {"chapter-order"}),
    ("NAV_ORDER as a plain assignment rather than an annotated one",
     lambda root: edit(root, HOOKS, "NAV_ORDER: dict[str, list[str]] =",
                       "NAV_ORDER ="),
     set()),
    ("a mkdocs_hooks.py with no NAV_ORDER to read",
     lambda root: edit(root, HOOKS, "NAV_ORDER:", "NAV_ORDR:"),
     {"chapter-order"}),
    ("a lesson with no ROADMAP row",
     lambda root: edit(root, ROADMAP,
                       "| [Beta](01_One/beta/README.md) | stub |\n", ""),
     {"roadmap-missing"}),
    ("a ROADMAP row for a page that is gone",
     lambda root: edit(root, ROADMAP, "(01_One/beta/README.md)",
                       "(01_One/gone/README.md)"),
     {"roadmap-missing"}),
    ("ROADMAP calling a written page a stub",
     lambda root: edit(root, ROADMAP,
                       "| [Alpha](01_One/alpha/README.md) | written, 2026-09-07 |",
                       "| [Alpha](01_One/alpha/README.md) | stub |"),
     {"roadmap-status"}),
    # The event this whole gate is about: a stub graduates and nothing else is
    # touched. One page changes; three files become wrong at once.
    ("a stub graduating, with no index updated", graduate,
     {"map-counts", "chapter-status", "roadmap-status"}),
]


def _names(tags: set) -> str:
    return ", ".join(sorted(tags)) if tags else "no problems"


def selftest() -> int:
    """Break one thing at a time and require exactly the right alarm.

    A selftest that scrambles everything proves only that *some* check fires,
    which cannot tell a load-bearing check from a decorative one. Each
    scenario below damages one thing and demands that its own check trips and
    the others stay quiet.

    It builds a miniature library rather than mutating this one, so it says
    the same thing while somebody else is mid-edit -- and so the last
    scenario, a stub graduating, can be played out for real.
    """
    print(f"selftest: {len(MUTATIONS)} states of a small library\n")
    failures = 0
    for label, mutate, expected in MUTATIONS:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "lib"
            build(root)
            mutate(root)
            fired = {tag for tag, _ in problems(root)}
        ok = fired == expected
        failures += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
        print(f"          expected {_names(expected)}, got {_names(fired)}")

    # --fix has to repair what it claims to, and touch nothing else.
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "lib"
        build(root)
        before = (root / "01_One/README.md").read_text(encoding="utf-8")
        edit(root, MAP_PAGE, "| 1 / 1 |", "| 9 / 9 |")
        changed = fix_counts(root)
        fixed = not [t for t, _ in problems(root) if t == "map-counts"]
        quiet = (root / "01_One/README.md").read_text(encoding="utf-8") == before
        ok = bool(changed) and fixed and quiet
        failures += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'}  --fix repairs a wrong count and "
              f"edits nothing else")
        print(f"          reported {changed or 'nothing'}; counts now "
              f"{'right' if fixed else 'STILL WRONG'}; chapter README "
              f"{'untouched' if quiet else 'MODIFIED'}")

    # And --fix must not paper over a defect that is not arithmetic: a
    # graduated stub still has to be reported, loudly, by the other two files.
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "lib"
        build(root)
        graduate(root)
        fix_counts(root)
        left = {tag for tag, _ in problems(root)}
        ok = left == {"chapter-status", "roadmap-status"}
        failures += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'}  --fix does not silence a "
              f"graduated stub's prose")
        print(f"          expected chapter-status, roadmap-status; got "
              f"{_names(left)}")

    print()
    if failures:
        print(f"selftest FAILED: {failures} case(s) did not produce the alarm "
              "they should. A check that survives its own mutation is not "
              "guarding anything.")
        return 1
    print(f"selftest ok: {len(MUTATIONS)} states plus two --fix cases, each "
          "defect caught by its own check and by no other.")
    return 0


# --------------------------------------------------------------------------

HELP = """\
  The chapter map in 00_Start_Here counts pages that live in other files, so it
  goes stale the day somebody writes one. Run --fix for the counts; the rest is
  prose and wants a person:

      python3 tools/check_chapter_status.py --fix

  A stub that graduates has to lose its notice AND gain a written status in its
  chapter README and in ROADMAP.md -- CONTRIBUTING.md, "Stubs", says both.

  A lesson table out of NAV_ORDER's order numbers its pages differently from
  the sidebar beside it. Decide which order you mean, then move the rows or the
  NAV_ORDER entries in mkdocs_hooks.py until the two agree -- CONTRIBUTING.md,
  "Nav order".
"""


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()

    if "--fix" in argv:
        changed = fix_counts(REPO)
        if changed:
            print(f"chapter status: rewrote {len(changed)} count(s) in {MAP_PAGE}")
            for line in changed:
                print(f"  {line}")
        else:
            print(f"chapter status: the counts in {MAP_PAGE} were already right")

    found = problems(REPO)
    if not found:
        tree = measure(REPO)
        pages = sum(len(v) for v in tree.values())
        stubs = sum(1 for v in tree.values() for stub in v.values() if stub)
        print(f"chapter status: {len(tree)} chapters, {pages} pages "
              f"({pages - stubs} written, {stubs} stubs) -- the map, the "
              f"chapter tables and ROADMAP all agree with the tree, and the "
              f"lesson tables read in NAV_ORDER's order.")
        return 0

    print("chapter status: the indexes and the tree disagree.\n")
    for _tag, problem in found:
        print(f"  {problem}")
    print()
    print(HELP.rstrip())
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
