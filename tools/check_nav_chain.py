#!/usr/bin/env python3
"""The sidebar and the prev/next arrows must tell the same story.

`mkdocs_hooks.py` states the reading order in NAV_ORDER and applies it in
on_nav(). That sorts the sidebar. It does NOT, on its own, move the arrows at
the foot of each page: MkDocs computes previous_page/next_page inside
get_navigation(), which runs before any hook, so a hook that only sorts leaves
the sidebar in reading order and the arrows in alphabetical order.

That was live here on all 13 chapters until 2026-09-07 -- the published
11_Tools page offered "awk" as its next page where NAV_ORDER says "grep" --
and nothing caught it, because each half is internally consistent and the two
are only comparable side by side. This gate compares them.

It walks the nav tree itself for the expected order rather than importing the
hook's own helper, so the fix is not being checked with the code under test.

It also checks a second, older hazard that `mkdocs_hooks.py` names in its own
comments twice: **an entry naming something that no longer exists is a silent
no-op.** `_order_key` simply never matches a stale name, and `LABEL_OVERRIDES`
never fires for a renamed folder, so a rename quietly demotes a page to the
alphabetical tail with nothing printed. (That second check came from a parallel
session that reached the same bug independently.)

    python3 tools/check_nav_chain.py

Needs the docs group (it loads MkDocs): run it under `uv run --group docs`,
which is how check_all.py and CI invoke it.
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


def _stale_entries() -> list[tuple[str, str | None, str]]:
    """NAV_ORDER / LABEL_OVERRIDES names with nothing on disk behind them."""
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
    # A label override is keyed by on-disk folder name, anywhere in the tree.
    folders = {d.name for d in REPO.rglob("*")
               if d.is_dir() and ".git" not in d.parts and "site" not in d.parts}
    for name in mkdocs_hooks.LABEL_OVERRIDES:
        if name not in folders:
            bad.append(("LABEL_OVERRIDES", None, name))
    return bad


def main() -> int:
    try:
        from mkdocs.config import load_config
        from mkdocs.structure.files import get_files
        from mkdocs.structure.nav import get_navigation
    except ImportError:
        print("check_nav_chain: MkDocs not importable -- run under "
              "`uv run --group docs`", file=sys.stderr)
        return 2

    config = load_config(str(REPO / "mkdocs.yml"))
    config.plugins.on_startup(command="build", dirty=False)
    files = get_files(config)
    files = config.plugins.on_files(files, config=config)
    nav = get_navigation(files, config)
    nav = config.plugins.on_nav(nav, config=config, files=files)

    stale = _stale_entries()
    if stale:
        print("nav tables name things that do not exist:\n")
        for table, key, name in stale:
            where = f"{table}[{key!r}]" if key is not None else table
            print(f"  {where} lists {name!r} -- no such file or folder")
        print("\n  These are silent no-ops: the hook skips a name it cannot")
        print("  match, so the page drops to the alphabetical tail and nothing")
        print("  is printed. Usually the tail of a rename.")
        return 1

    sidebar = walk(nav.items)
    if not sidebar:
        print("check_nav_chain: the nav has no pages -- nothing to check",
              file=sys.stderr)
        return 2

    # Follow next_page from the first page and see where it lands.
    chain, seen, page = [], set(), sidebar[0]
    while page is not None and id(page) not in seen:
        seen.add(id(page))
        chain.append(page)
        page = page.next_page

    def uri(p) -> str:
        return p.file.src_uri

    if [uri(p) for p in chain] == [uri(p) for p in sidebar]:
        print(f"nav chain: the arrows follow the sidebar, all "
              f"{len(sidebar)} pages.")
        return 0

    print("nav chain: the prev/next arrows do NOT follow the sidebar.\n")
    print("  This is the failure mkdocs_hooks.on_nav re-chains against: the")
    print("  sidebar is sorted by NAV_ORDER, the arrows are not. Check that")
    print("  on_nav still reassigns previous_page/next_page after _visit().\n")
    for i, (want, got) in enumerate(zip(sidebar, chain)):
        if uri(want) != uri(got):
            print(f"  first divergence at position {i}:")
            print(f"    sidebar says  {uri(want)}")
            print(f"    arrows say    {uri(got)}")
            break
    else:
        print(f"  the arrows reach {len(chain)} pages, the sidebar has "
              f"{len(sidebar)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
