#!/usr/bin/env python3
"""A #fragment has to name the same heading on GitHub as on the site.

This library is read on two surfaces, and each gives a heading its id by a
rule of its own. The site's is Python-Markdown's toc slugify, pinned in
uv.lock: fold to ASCII, delete everything but letters, digits, `_`, `-` and
whitespace, lowercase, and collapse each run of hyphens and whitespace into a
single hyphen. GitHub's deletes the same punctuation and stops there: it
lowercases, keeps letters, marks, digits, `_`, hyphens and spaces, folds
nothing, collapses nothing, and writes a hyphen for every space. Most headings
come out the same both ways. The commonest one that does not is ordinary
prose:

    ## MSB and LSB — the abbreviation does not say which
       site    #msb-and-lsb-the-abbreviation-does-not-say-which
       GitHub  #msb-and-lsb--the-abbreviation-does-not-say-which

Both delete the dash, which leaves two spaces; the site collapses them and
GitHub writes a hyphen for each. No fragment reaches that heading on both
surfaces. Measured against GitHub's own renderer on 2026-09-11, at ce26c2f:
116 of the 1,498 headings on the 138 pages both surfaces build from the same
Markdown had two ids -- 111 because a punctuation mark stood alone between
spaces, 109 of those a ` — `, and 5 because a hyphen of the heading's own sat
beside a space (`uni -h`) or a mark opened it (`= is the length`). A repeat
parts company too -- the second `## In Python` is `#in-python_1` on the site
and `#in-python-1` on GitHub -- and so does any letter outside ASCII, which the
site folds or drops: `## Łódź` is `#odz` against `#łódź`.

`mkdocs build --strict` holds a fragment to the site's ids and to nothing else,
so a link to one of those headings builds green while GitHub opens the top of
the page. One of the 209 fragment links at ce26c2f did, from 11_Tools/uni_help
to the heading above, until the heading took a colon -- which kept the site's
id and gave GitHub the same one. This is the other half: for every #fragment
link outside code, the heading it names on the site must carry the same id on
GitHub.

A fragment that names no heading at all is reported as well. MkDocs reports
that too, but it keeps fragment links only when it logs above DEBUG, so a
build run with -v checks none of them: planted on 2026-09-11,
`../preparing_a_string/README.md#no-such-heading` built green under
--strict -v. This reads the Markdown, so it fails that link at any logging
level. A link to a folder is read as a link to its README.md, which is what
both surfaces serve there; `mkdocs --strict` has refused a folder link
outright since the same day.

Both rules are reimplemented from what the renderers did, not from their
documentation, and held to them: at ce26c2f these functions gave every one of
GitHub's 1,506 ids on the library's 140 pages, and every one of the site's
on every page but index.md, whose site version inlines README.md. Two details
depart from html-pipeline's TocFilter as it is usually described, and both
were measured rather than assumed: GitHub keeps digits but not every number
(`²` and `½` go, `Ⅳ` stays), and a repeat skips any id already given out, so
`## In Python 1` after two `## In Python` is `#in-python-1-1`. Every row of
IDS and CASES below was rendered on both surfaces before it went in -- GitHub's
through its /markdown API, whose anchors matched its page view, and the
site's through a Markdown built from this repo's mkdocs.yml -- so each states
a measured fact.

Not read: a raw `<a href>`, and a setext heading (text underlined with `=` or
`-`). Nor the two lines the renderers disagree are headings at all, measured
the same day: `#word`, with no space, is a heading on the site only, and a
heading indented by one to three spaces is one on GitHub only -- this reads
them as GitHub does. The library has none of these; its heading counts
matched both renderers'.

    python3 tools/check_fragments.py
    python3 tools/check_fragments.py --selftest
"""

from __future__ import annotations

import html
import pathlib
import posixpath
import re
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

REPO = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = {"site", "__pycache__", "target"}  # and every directory whose name starts with "."

FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
ATX = re.compile(r"^ {0,3}(#{1,6})(?=[ \t]|$)(.*)$")
CLOSING_HASHES = re.compile(r"(?:^|[ \t]+)#+[ \t]*$")
ESCAPABLE = frozenset("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")

# Inline Markdown inside a heading, reduced to the text both renderers slug.
_LABEL = r"\[((?:[^\[\]]|\[[^\[\]]*\])*)\]"
_DEST = r"\(\s*(<[^>\n]*>|(?:[^\s()]|\([^\s()]*\))*)(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)"
IMAGE = re.compile(r"!" + _LABEL + _DEST)
LINK = re.compile(_LABEL + _DEST)
REF_LINK = re.compile(_LABEL + r"\[[^\[\]]*\]")
AUTOLINK = re.compile(r"<((?:https?|ftp|mailto):[^<>\s]*)>")
TAG = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>]*)?/?>")
ENTITY = re.compile(r"&(?:#[0-9]{1,7}|#[xX][0-9a-fA-F]{1,6}|[A-Za-z][A-Za-z0-9]{1,31});")
EMPHASIS = [
    re.compile(r"(\*{1,3})(?!\s)(.+?)(?<!\s)\1"),
    re.compile(r"(?<!\w)(_{1,3})(?!\s)(.+?)(?<!\s)\1(?!\w)"),
]
KEPT = re.compile("\x00([0-9]+)\x01")

# Links, on a line with its code spans removed.
CODE_SPAN = re.compile(r"(`+)(?!`).*?(?<!`)\1(?!`)")
MD_LINK = re.compile(r"(!?)" + _LABEL + _DEST)
REF_DEF = re.compile(r"^ {0,3}\[[^\]]+\]:\s*(<[^>]*>|\S+)")


def prose_lines(text: str):
    """Yield (line number, line) for each line outside fences and HTML comments."""
    fence = None
    in_comment = False
    for n, line in enumerate(text.split("\n"), 1):
        if fence is not None:
            if re.fullmatch(rf"[ \t]*{re.escape(fence[0])}{{{len(fence)},}}[ \t]*", line):
                fence = None
            continue
        if in_comment:
            end = line.find("-->")
            if end == -1:
                continue
            line, in_comment = line[end + 3:], False
        else:
            m = FENCE.match(line)
            if m and not (m.group(1)[0] == "`" and "`" in line[m.end():]):
                fence = m.group(1)
                continue
        line = re.sub(r"<!--.*?-->", "", line)
        start = line.find("<!--")
        if start != -1:
            line, in_comment = line[:start], True
        yield n, line


def rendered_text(src: str) -> str:
    """The text a heading's inline Markdown renders to, which is what gets slugged."""
    kept: list[str] = []

    def keep(s: str) -> str:
        kept.append(s)
        return f"\x00{len(kept) - 1}\x01"

    out, i = [], 0
    while i < len(src):
        c = src[i]
        if c == "\\" and i + 1 < len(src) and src[i + 1] in ESCAPABLE:
            out.append(keep(src[i + 1]))
            i += 2
        elif c == "`":
            ticks = re.match(r"`+", src[i:]).group()
            close = re.compile(rf"(?<!`){ticks}(?!`)").search(src, i + len(ticks))
            if close is None:
                out.append(ticks)
                i += len(ticks)
            else:
                code = src[i + len(ticks):close.start()]
                if code.startswith(" ") and code.endswith(" ") and code.strip(" "):
                    code = code[1:-1]
                out.append(keep(code))
                i = close.end()
        else:
            out.append(c)
            i += 1
    text = "".join(out)
    text = IMAGE.sub("", text)
    text = LINK.sub(r"\1", text)
    text = REF_LINK.sub(r"\1", text)
    text = AUTOLINK.sub(r"\1", text)
    text = TAG.sub("", text)
    text = ENTITY.sub(lambda m: html.unescape(m.group()), text)
    for pattern in EMPHASIS:
        while True:
            new = pattern.sub(r"\2", text)
            if new == text:
                break
            text = new
    return KEPT.sub(lambda m: kept[int(m.group(1))], text).strip()


def headings(text: str) -> list[tuple[int, str]]:
    """(line number, rendered text) of every ATX heading outside code."""
    found = []
    for n, line in prose_lines(text):
        m = ATX.match(line)
        if m:
            content = CLOSING_HASHES.sub("", m.group(2).strip())
            found.append((n, rendered_text(content)))
    return found


def site_slug(text: str) -> str:
    """Python-Markdown's toc.slugify(text, "-"), after its strip_tags() whitespace collapse."""
    value = unicodedata.normalize("NFKD", " ".join(text.split()))
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)


# The categories GitHub keeps besides `-` and space: letters, marks, digits,
# letter-numbers and connector punctuation. Nl is in because `Ⅳ` survived; No
# is out because `²` and `½` did not -- IDS below has the row.
WORD = {"Lu", "Ll", "Lt", "Lm", "Lo", "Mn", "Mc", "Me", "Nd", "Nl", "Pc"}


def github_slug(text: str) -> str:
    """GitHub's: lowercase, keep WORD, `-` and ` `, and write `-` for each ` `."""
    keep = "".join(c for c in text.lower() if c in "- " or unicodedata.category(c) in WORD)
    return keep.replace(" ", "-")


def site_ids(texts: list[str]) -> list[str]:
    """Python-Markdown's unique(): a repeat gets _1, _2, ... and so does an empty id."""
    used: set[str] = set()
    out = []
    for text in texts:
        slug = site_slug(text)
        while slug in used or not slug:
            m = re.match(r"^(.*)_([0-9]+)$", slug)
            slug = f"{m.group(1)}_{int(m.group(2)) + 1}" if m else f"{slug}_1"
        used.add(slug)
        out.append(slug)
    return out


def github_ids(texts: list[str]) -> list[str]:
    """GitHub's: a repeat gets -1, -2, ..., skipping any id already given out."""
    given: dict[str, int] = {}
    out = []
    for text in texts:
        slug = base = github_slug(text)
        while slug in given:
            given[base] += 1
            slug = f"{base}-{given[base]}"
        given[slug] = 0
        out.append(slug)
    return out


def fragment_links(text: str) -> list[tuple[int, str]]:
    """(line number, href) of every link with a #fragment, outside code."""
    found = []
    for n, line in prose_lines(text):
        line = CODE_SPAN.sub("", line)
        m = REF_DEF.match(line)
        if m and "#" in m.group(1):
            found.append((n, m.group(1).strip("<>")))
        for m in MD_LINK.finditer(line):
            href = m.group(3).strip("<>")
            if not m.group(1) and "#" in href:
                found.append((n, href))
    return found


def resolve(page: str, href: str, pages: dict[str, str]) -> tuple[str, str] | None:
    """(target page, fragment) for a link into the library, or None for any other link."""
    parts = urlsplit(href)
    if parts.scheme or parts.netloc or not parts.fragment:
        return None
    path = unquote(parts.path)
    if not path:
        return page, unquote(parts.fragment)
    target = posixpath.normpath(posixpath.join(posixpath.dirname(page), path))
    if f"{target}/README.md" in pages:
        target = f"{target}/README.md"
    if not target.endswith(".md"):
        return None
    return target, unquote(parts.fragment)


def check(pages: dict[str, str]) -> tuple[int, list[str]]:
    """(fragment links checked, findings) over {path from the root: Markdown}."""
    ids: dict[str, list[tuple[int, str, str, str]]] = {}

    def targets(rel: str) -> list[tuple[int, str, str, str]]:
        if rel not in ids:
            found = headings(pages[rel])
            texts = [t for _, t in found]
            ids[rel] = [(n, t, s, g) for (n, t), s, g
                        in zip(found, site_ids(texts), github_ids(texts))]
        return ids[rel]

    checked, bad = 0, []
    for rel in sorted(pages):
        for n, href in fragment_links(pages[rel]):
            hit = resolve(rel, href, pages)
            if hit is None:
                continue
            target, fragment = hit
            checked += 1
            where = f"{rel}:{n}: [{href}]"
            if target not in pages:
                bad.append(f"{where} names {target}, which is not a page in the library.")
                continue
            heads = targets(target)
            on_site = [h for h in heads if h[2] == fragment]
            if on_site:
                line, text, _, gh = on_site[0]
                if gh != fragment:
                    bad.append(
                        f"{where} is the site's id for {text!r} ({target}:{line}), but "
                        f"GitHub's id for that heading is #{gh}, so on GitHub the link "
                        "opens the top of the page.")
                continue
            on_github = [h for h in heads if h[3] == fragment]
            if on_github:
                line, text, site, _ = on_github[0]
                bad.append(
                    f"{where} is GitHub's id for {text!r} ({target}:{line}), but the "
                    f"site's is #{site}, so on the site the link opens the top of the page.")
            else:
                bad.append(f"{where} names no heading in {target}.")
    return checked, bad


def library() -> dict[str, str]:
    """Every Markdown page, by its path from the repository root."""
    found = {}
    for p in sorted(REPO.rglob("*.md")):
        rel = p.relative_to(REPO)
        if any(part.startswith(".") or part in SKIP_DIRS for part in rel.parts[:-1]):
            continue
        found[rel.as_posix()] = p.read_text(encoding="utf-8")
    return found


# (heading as written, the site's id, GitHub's id), each read off both
# renderers on 2026-09-11 -- GitHub's through its /markdown API, which gave the
# same anchors as its page view, and the site's through a Markdown built from
# this repo's own mkdocs.yml. So every row is a measurement, not a reading of
# either rule's documentation.
IDS = [
    ("MSB and LSB: the abbreviation does not say which",
     "msb-and-lsb-the-abbreviation-does-not-say-which",
     "msb-and-lsb-the-abbreviation-does-not-say-which"),
    ("MSB and LSB — the abbreviation does not say which",
     "msb-and-lsb-the-abbreviation-does-not-say-which",
     "msb-and-lsb--the-abbreviation-does-not-say-which"),
    ("--pre and -z", "-pre-and-z", "--pre-and--z"),
    ("trailing hyphen -", "trailing-hyphen-", "trailing-hyphen--"),
    ("ÉCOLE and Straße", "ecole-and-strae", "école-and-straße"),
    ("x² and ½ and Ⅳ", "x2-and-12-and-iv", "x-and--and-ⅳ"),
    ("tab\there", "tab-here", "tabhere"),
    ("nbsp\u00a0here", "nbsp-here", "nbsphere"),
    ("An ![alt text](x.png) image", "an-image", "an--image"),
    ("Tom &amp; Jerry &copy; 2026", "tom-jerry-2026", "tom--jerry--2026"),
    ("__init__ and `__init__`", "init-and-__init__", "init-and-__init__"),
    ("<kbd>Ctrl</kbd>+<kbd>C</kbd>", "ctrlc", "ctrlc"),
    ("—", "_1", ""),
]

# (what it shows, the target page's headings, the link, where the link sits,
# whether it must be reported). Each target is a README.md under t/ and each
# link sits on a page beside t/ -- or on t/README.md itself, for "same".
CASES = [
    ("a colon: one id on both surfaces",
     "## MSB and LSB: the abbreviation does not say which",
     "[x](t/README.md#msb-and-lsb-the-abbreviation-does-not-say-which)", "page", False),
    ("an em dash between spaces: a second hyphen on GitHub",
     "## MSB and LSB — the abbreviation does not say which",
     "[x](t/README.md#msb-and-lsb-the-abbreviation-does-not-say-which)", "page", True),
    ("the same heading by GitHub's id, which the site does not have",
     "## MSB and LSB — the abbreviation does not say which",
     "[x](t/README.md#msb-and-lsb--the-abbreviation-does-not-say-which)", "page", True),
    ("a hyphen of the text's own beside a space",
     "## uni -h, line by line", "[x](t/README.md#uni-h-line-by-line)", "page", True),
    ("the first of two equal headings",
     "## In Python\n\n## In Python", "[x](t/README.md#in-python)", "page", False),
    ("the second of two equal headings: _1 on the site, -1 on GitHub",
     "## In Python\n\n## In Python", "[x](t/README.md#in-python_1)", "page", True),
    ("a heading whose own id is a suffix GitHub already gave out",
     "## In Python\n\n## In Python\n\n## In Python 1",
     "[x](t/README.md#in-python-1)", "page", True),
    ("a letter outside ASCII", "## Łódź", "[x](t/README.md#odz)", "page", True),
    ("a heading with no letter or digit in it", "## —", "[x](t/README.md#_1)", "page", True),
    ("underscores that are emphasis, which both renderers drop",
     "## A _word_ here", "[x](t/README.md#a-word-here)", "page", False),
    ("code, a link and inline HTML inside the heading",
     "## `LC_ALL=C`, [a link](x.md) and <kbd>Ctrl</kbd>",
     "[x](t/README.md#lc_allc-a-link-and-ctrl)", "page", False),
    ("a fragment that names no heading",
     "## In Python", "[x](t/README.md#no-such-heading)", "page", True),
    ("a link to the folder, checked against its README.md",
     "## uni -h, line by line", "[x](t/#uni-h-line-by-line)", "page", True),
    ("a link to the same page",
     "## uni -h, line by line", "[x](#uni-h-line-by-line)", "same", True),
    ("a real link beside a code span",
     "## uni -h, line by line",
     "`code` then [x](t/README.md#uni-h-line-by-line)", "page", True),
    ("a link inside a code span is not a link",
     "## uni -h, line by line", "`[x](t/README.md#uni-h-line-by-line)`", "page", False),
    ("a link inside a fence is not a link",
     "## uni -h, line by line",
     "```text\n[x](t/README.md#uni-h-line-by-line)\n```", "page", False),
]


def selftest() -> int:
    """Hold both rules to the ids the renderers gave, then plant one link at a time."""
    print("selftest: each heading's two ids, as both renderers gave them\n")
    wrong = 0
    for src, site, github in IDS:
        (_, text), = headings(f"## {src}")
        got = (site_ids([text])[0], github_ids([text])[0])
        ok = got == (site, github)
        wrong += not ok
        print(f"  {'ok  ' if ok else 'FAIL'}  {src!r}: site #{site}, GitHub #{github}")
        if not ok:
            print(f"          computed site #{got[0]}, GitHub #{got[1]}")

    print("\nselftest: one link at a time, to a page built for it\n")
    for name, target, link, where, must_report in CASES:
        if where == "same":
            pages = {"t/README.md": f"# T\n\n{target}\n\n{link}\n"}
        else:
            pages = {"t/README.md": f"# T\n\n{target}\n", "page.md": f"# Page\n\n{link}\n"}
        _, bad = check(pages)
        ok = bool(bad) == must_report
        wrong += not ok
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
        if not ok:
            print(f"          expected {'a report' if must_report else 'silence'}, "
                  f"got {bad[0] if bad else 'silence'}")

    total = len(IDS) + len(CASES)
    print()
    if wrong:
        print(f"selftest FAILED: {wrong} of {total} cases wrong.")
        return 1
    print(f"selftest ok: {len(IDS)} headings given both renderers' ids, and "
          f"{sum(c[4] for c in CASES)} of {len(CASES)} planted links reported, "
          "exactly the ones that must be.")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    checked, bad = check(library())
    if not bad:
        print(f"fragments: {checked} #fragment links, each naming one heading by the "
              "same id on GitHub and on the site.")
        return 0
    print(f"fragments: {len(bad)} of {checked} #fragment links do not name one heading "
          "by the same id on both surfaces.\n")
    for line in bad:
        print(f"  {line}")
    print("\n  Reword the heading so its two ids agree -- ': ' in place of ' — ' keeps the "
          "site's id -- or link a heading whose ids already do. CONTRIBUTING.md, "
          "'Links', has why.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
