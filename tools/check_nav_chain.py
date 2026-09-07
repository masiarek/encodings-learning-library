#!/usr/bin/env python3
"""The sidebar and the footer arrows must tell the same story.

`NAV_ORDER` in `mkdocs_hooks.py` states the reading order and `on_nav` applies
it. Sorting `nav.items` fixes the **sidebar**. It does not, on its own, fix the
two arrows at the foot of the page: MkDocs sets every page's `previous_page` /
`next_page` inside `get_navigation()`, which runs *before* any hook, so a hook
that only re-sorts leaves the arrows walking the default alphabetical order.

That shipped on all thirteen chapters until 2026-09-07 -- the published
`11_Tools` page offered *awk* as the page after it while the sidebar beside it
read *grep* first. Nothing caught it because each half is internally
consistent, `--strict` has no opinion about a hook that reorders a nav without
re-linking it, and only a reader who already knew what came next could tell.

This gate checks three things, and walks the nav itself rather than importing
the hook's helper, so the fix is not checked with the code under test:

1. **The forward chain follows the sidebar.** `next_page` from the first page
   must visit exactly the pages a depth-first walk of the sidebar visits, in
   that order.
2. **`previous_page` mirrors it.** The hook sets both in one loop today, so
   they cannot diverge now -- but a half-rebuilt chain is precisely the
   regression this gate exists to catch, so it is asserted rather than assumed.
3. **`nav.pages` matches.** `on_nav` promises to rewrite it; templates and
   plugins read it.

Plus a fourth, older hazard that `mkdocs_hooks.py` flags in its own comments
twice: **an entry naming something that no longer exists is a silent no-op.**
`_order_key` never matches a stale name and `LABEL_OVERRIDES` never fires for a
renamed folder, so the page quietly drops to the alphabetical tail with nothing
printed. (That check came from a parallel session that reached the same bug.)

    python3 tools/check_nav_chain.py
    python3 tools/check_nav_chain.py --selftest   # mutate each check in turn

Needs the docs group: run under `uv run --group docs`, which is how
`check_all.py` and CI invoke it.
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent


def walk(items: list) -> list:
    """Pages under `items`, depth-first -- the order the sidebar renders."""
    out = []
    for item in items:
        if item.is_page:
            out.append(item)
        elif item.is_section:
            out.extend(walk(item.children))
    return out


def uri(page) -> str:
    """Compare pages by source path: Page defines __eq__ but not __hash__."""
    return page.file.src_uri


def _names(tags: set) -> str:
    """Render a set of problem tags for the selftest's expected/got columns."""
    return ", ".join(sorted(tags)) if tags else "no problems"


def build_nav():
    from mkdocs.config import load_config
    from mkdocs.structure.files import get_files
    from mkdocs.structure.nav import get_navigation

    config = load_config(str(REPO / "mkdocs.yml"))
    config.plugins.on_startup(command="build", dirty=False)
    files = config.plugins.on_files(get_files(config), config=config)
    nav = get_navigation(files, config)
    return config.plugins.on_nav(nav, config=config, files=files)


def follow(start, attr: str) -> list:
    """Follow `attr` from `start` until it ends or repeats."""
    out, seen, page = [], set(), start
    while page is not None and id(page) not in seen:
        seen.add(id(page))
        out.append(page)
        page = getattr(page, attr)
    return out


def check_chain(nav) -> list[tuple[str, str]]:
    """Problems with the prev/next chain, as (tag, message).

    The tag names which of the three assertions failed. `--selftest` needs
    that: proving a check is load-bearing means showing a defect trips *that*
    check and leaves the others quiet, which a list of prose cannot express.
    An empty list means all three hold.
    """
    sidebar = walk(nav.items)
    if not sidebar:
        return [("empty", "the nav has no pages -- nothing to check")]
    problems = []

    forward = [uri(p) for p in follow(sidebar[0], "next_page")]
    want = [uri(p) for p in sidebar]
    if forward != want:
        detail = f"the arrows reach {len(forward)} pages, the sidebar has {len(want)}"
        for i, (a, b) in enumerate(zip(want, forward)):
            if a != b:
                detail = (f"first divergence at position {i}:\n"
                          f"    sidebar says  {a}\n"
                          f"    arrows say    {b}")
                break
        problems.append(
            ("next", "next_page does not follow the sidebar -- " + detail))

    backward = [uri(p) for p in follow(sidebar[-1], "previous_page")]
    if backward != want[::-1]:
        problems.append((
            "previous",
            f"previous_page is not the mirror of next_page: it reaches "
            f"{len(backward)} pages walking back from {want[-1]}, expected "
            f"{len(want)}"))

    if [uri(p) for p in nav.pages] != want:
        problems.append((
            "pages",
            "nav.pages is not in sidebar order -- on_nav promises to rewrite "
            "it, and templates and plugins read it"))

    return problems


def stale_entries() -> list[tuple[str, str | None, str]]:
    """NAV_ORDER / LABEL_OVERRIDES names with nothing behind them."""
    sys.path.insert(0, str(REPO))
    import mkdocs_hooks

    bad: list[tuple[str, str | None, str]] = []
    for key, names in mkdocs_hooks.NAV_ORDER.items():
        base = REPO / key if key else REPO
        if not base.is_dir():
            bad.append(("NAV_ORDER", None, key))
            continue
        for name in names:
            if not (base / name).exists():
                bad.append(("NAV_ORDER", key, name))
    folders = {d.name for d in REPO.rglob("*")
               if d.is_dir() and ".git" not in d.parts and "site" not in d.parts}
    for name in mkdocs_hooks.LABEL_OVERRIDES:
        if name not in folders:
            bad.append(("LABEL_OVERRIDES", None, name))
    return bad


def selftest() -> int:
    """Break one thing at a time and require exactly the right alarm.

    A selftest that scrambles the whole chain at once proves only that *some*
    assertion fires. It cannot tell a load-bearing check from a decorative
    one -- and two of the four checks here were added on the argument that
    they guard a regression that cannot happen *yet*, which is exactly the
    kind of claim that rots into a no-op unnoticed. So each scenario below
    damages one thing and demands that the matching check trips and the
    others stay silent. An assertion that never fails its own mutation is
    not protecting anything.

    Where the correct state comes from matters. It is snapshotted from the
    hook's own output and restored between scenarios, never re-derived here,
    so the gate keeps its rule of not checking the fix with the code under
    test. The mutations damage a correct nav; they do not construct one.
    """
    sys.path.insert(0, str(REPO))
    import mkdocs_hooks

    nav = build_nav()
    sidebar = walk(nav.items)
    if len(sidebar) < 3:
        print(f"selftest INCONCLUSIVE: {len(sidebar)} page(s) in the nav is "
              "too few to mutate meaningfully.")
        return 1

    alphabetical = sorted(sidebar, key=uri)
    if [uri(p) for p in alphabetical] == [uri(p) for p in sidebar]:
        print("selftest INCONCLUSIVE: NAV_ORDER currently matches alphabetical "
              "order, so every mutation below would be a no-op.")
        return 1

    # The truth, taken from on_nav rather than rebuilt.
    chain = [(page, page.previous_page, page.next_page) for page in sidebar]
    pages_order = list(nav.pages)

    def restore() -> None:
        for page, previous, following in chain:
            page.previous_page, page.next_page = previous, following
        nav.pages[:] = pages_order

    def break_next() -> None:
        for i, page in enumerate(alphabetical):
            page.next_page = alphabetical[i + 1] if i + 1 < len(alphabetical) else None

    def break_previous() -> None:
        for i, page in enumerate(alphabetical):
            page.previous_page = alphabetical[i - 1] if i else None

    def break_pages() -> None:
        nav.pages[:] = alphabetical

    def break_everything() -> None:
        break_next()
        break_previous()
        break_pages()

    scenarios = [
        ("the hook's own output, unmutated", lambda: None, set()),
        ("next_page re-chained alphabetically", break_next, {"next"}),
        ("previous_page re-chained alphabetically", break_previous, {"previous"}),
        ("nav.pages reordered alphabetically", break_pages, {"pages"}),
        ("all three -- the shape that shipped for 13 chapters",
         break_everything, {"next", "previous", "pages"}),
    ]

    print(f"selftest: {len(scenarios) + 1} mutations of a correct "
          f"{len(sidebar)}-page nav\n")
    failures = 0
    for label, mutate, expected in scenarios:
        restore()
        mutate()
        fired = {tag for tag, _ in check_chain(nav)}
        ok = fired == expected
        failures += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
        print(f"          expected {_names(expected)}, got {_names(fired)}")
    restore()

    # The fourth check reads NAV_ORDER, not the nav, so it is mutated at the
    # table. This is the check that caught a real blocker on the day it
    # landed: an entry committed ahead of the folder it names.
    ghost = "no_such_page__selftest_only.md"
    saved = mkdocs_hooks.NAV_ORDER
    mkdocs_hooks.NAV_ORDER = {**saved, "": [*saved.get("", []), ghost]}
    try:
        caught = any(name == ghost for _, _, name in stale_entries())
    finally:
        mkdocs_hooks.NAV_ORDER = saved
    failures += 0 if caught else 1
    print(f"  {'ok  ' if caught else 'FAIL'}  NAV_ORDER naming a file that "
          "does not exist")
    print(f"          expected the injected name to be reported, "
          f"{'it was' if caught else 'IT WAS NOT'}")

    if failures:
        print(f"\nselftest FAILED: {failures} mutation(s) did not produce the "
              "alarm they should. A check that survives its own mutation is "
              "not guarding anything.")
        return 1
    print(f"\nselftest ok: {len(scenarios) + 1} mutations, each defect caught "
          "by its own check and by no other.")
    return 0


def main(argv: list[str]) -> int:
    try:
        import mkdocs  # noqa: F401
    except ImportError:
        print("check_nav_chain: MkDocs not importable -- run under "
              "`uv run --group docs`", file=sys.stderr)
        return 2

    if "--selftest" in argv:
        return selftest()

    stale = stale_entries()
    if stale:
        print("nav tables name things that do not exist:\n")
        for table, key, name in stale:
            where = f"{table}[{key!r}]" if key is not None else table
            print(f"  {where} lists {name!r} -- no such file or folder")
        print("\n  These are silent no-ops: the hook skips a name it cannot")
        print("  match, so the page drops to the alphabetical tail and")
        print("  nothing is printed.\n")
        print("  Two ways this happens. A rename left the entry behind --")
        print("  update it. Or the folder exists on disk but is not committed")
        print("  yet, in which case the entry is ahead of its page: commit")
        print("  them together, as CONTRIBUTING's 'Nav order' section says.")
        return 1

    nav = build_nav()
    problems = check_chain(nav)
    if not problems:
        print(f"nav chain: the arrows follow the sidebar, both ways, all "
              f"{len(nav.pages)} pages.")
        return 0

    print("nav chain: the sidebar and the arrows disagree.\n")
    print("  Check that mkdocs_hooks.on_nav still reassigns previous_page,")
    print("  next_page and nav.pages after _visit() re-sorts the tree.\n")
    for _tag, problem in problems:
        print(f"  {problem}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
