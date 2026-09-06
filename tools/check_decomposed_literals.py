#!/usr/bin/env python3
"""A string called decomposed has to actually be decomposed.

House rule (CONTRIBUTING.md -> The cast): when a line calls a literal *decomposed*
or *NFD*, that literal must carry a real combining mark -- or the line must spell
the mark out (`U+0301`, `\\u{301}`, `65 cc 81`, `\\314\\201`), which is the better
answer inside a fence, where a bare mark is invisible to the author too.

Why this one needs a machine. `café` and `café` are the same picture:
no page, no diff and no reviewer can tell them apart, and the odds run one way --
**you cannot type a decomposed string**. Keyboard, editor and clipboard all hand
you the composed spelling, so a hand-written "decomposed" example is composed
unless somebody deliberately pasted a mark. When this rule was written down, all
three of the library's hand-authored decomposed literals were composed, and each
sat under numbers (6 bytes, 5 code points) that its own string does not produce.

Scope, deliberately narrow, so that a hit is always a real defect:

  * Hand-authored Markdown only. Generated blocks (`<!-- output: -->`,
    `<!-- source: -->`) are skipped -- they are checked against the program that
    printed them by `run_examples.py --check`, which is a stronger gate, and a
    program may legitimately print a composed *label* beside computed counts.
  * The label has to be next to the literal (within ADJACENT characters). Prose
    that names a string and its two spellings in one breath -- "creating `zolw`
    in NFC and again in NFD" -- is making no claim about that literal and is not
    an offender.
  * Fences ARE searched. The defect this was written for lived in one.

What it does not check: the other direction (a decomposed literal labelled
composed), which cannot happen by accident for the same keyboard reason; and
per-literal attribution on a line that shows a pair -- one real mark anywhere on
the line satisfies it.

    python3 tools/check_decomposed_literals.py             # exit 1 on a literal that lies
    python3 tools/check_decomposed_literals.py --selftest  # prove the check still bites
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"site", ".venv", ".git", "__pycache__", "target"}

# How close the label has to sit to the literal before it is a claim about it.
# "`cafe` (decomposed)" is 2 characters; "`zolw` in NFC and again in NFD" is 21.
ADJACENT = 12

TRIGGER = re.compile(r"\b(?:decomposed|decomposition|NFD)\b", re.IGNORECASE)

# Delimited literals: backticks, straight quotes, curly quotes.
LITERAL = re.compile(
    r"`(?P<b>[^`\n]{1,60})`"
    r"|\"(?P<d>[^\"\n]{1,60})\""
    r"|'(?P<s>[^'\n]{1,60})'"
    r"|“(?P<cd>[^”\n]{1,60})”"
)

GEN_OPEN = re.compile(r"<!--\s*(?:output|source):")
GEN_CLOSE = re.compile(r"<!--\s*/(?:output|source)\s*-->")

# Spellings of a code point, so a page may write the mark instead of showing it.
HEX_CP = re.compile(r"(?:U\+|\\u\{?)([0-9A-Fa-f]{2,6})\}?")
BYTE = re.compile(r"\\x([0-9A-Fa-f]{2})|\\([0-3][0-7]{2})|\b([0-9A-Fa-f]{2})\b")


def pages() -> list[Path]:
    return [
        p
        for p in sorted(REPO.rglob("*.md"))
        if not any(part in SKIP_DIRS for part in p.relative_to(REPO).parts)
    ]


def is_precomposed(ch: str) -> bool:
    """True for a character with a canonical decomposition -- e, z, o.

    Compatibility decompositions (`fi` -> f + i) are excluded: they are a
    different normalization form and never the subject of these lines.
    """
    d = unicodedata.decomposition(ch)
    return bool(d) and not d.startswith("<")


def spells_a_mark(line: str) -> bool:
    """True if the line writes a combining code point out instead of showing it."""
    for m in HEX_CP.finditer(line):
        try:
            if unicodedata.combining(chr(int(m.group(1), 16))):
                return True
        except (ValueError, OverflowError):
            pass
    raw = bytearray()
    for m in BYTE.finditer(line):
        hexpair, octal, bare = m.group(1), m.group(2), m.group(3)
        if octal is not None:
            raw.append(int(octal, 8))
        else:
            raw.append(int(hexpair or bare, 16))
    return any(unicodedata.combining(c) for c in raw.decode("utf-8", "ignore"))


def offending_literals(line: str) -> list[str]:
    """Literals on this line that are called decomposed and are not."""
    if not TRIGGER.search(line):
        return []
    if any(unicodedata.combining(c) for c in line) or spells_a_mark(line):
        return []
    labels = [(m.start(), m.end()) for m in TRIGGER.finditer(line)]
    found = []
    for m in LITERAL.finditer(line):
        text = next(g for g in m.groups() if g is not None)
        if not any(is_precomposed(c) for c in text):
            continue
        near = any(
            start - m.end() <= ADJACENT and m.start() - end <= ADJACENT
            for start, end in labels
        )
        if near:
            found.append(text)
    return found


def scan() -> int:
    offenders: list[str] = []
    for page in pages():
        generated = False
        for n, line in enumerate(page.read_text(encoding="utf-8").splitlines(), 1):
            if GEN_CLOSE.search(line):
                generated = False
                continue
            if GEN_OPEN.search(line):
                generated = True
            if generated:
                continue
            for literal in offending_literals(line):
                rel = page.relative_to(REPO)
                offenders.append(f"{rel}:{n}: {literal!r} in: {line.strip()[:88]}")

    if not offenders:
        print("decomposed literals: every string called decomposed carries its mark.")
        return 0

    print(f"decomposed literals: {len(offenders)} literal(s) labelled decomposed but composed.\n")
    print("Fix by pasting the real spelling, or by writing the mark out:")
    print("  python3 -c \"import unicodedata as u; print(u.normalize('NFD', 'café'))\"\n")
    for line in offenders[:40]:
        print("  " + line)
    if len(offenders) > 40:
        print(f"  … and {len(offenders) - 40} more")
    return 1


# The three defects this was written for, verbatim as they sat on disk, plus the
# lines that must NOT fire. A checker nobody can see fail is a checker that has
# quietly stopped checking.
COMPOSED = "caf\u00e9"
DECOMPOSED = "cafe\u0301"

MUST_FLAG = [
    f'   "{COMPOSED}" (decomposed)      6 bytes    5 code points    4 things a person sees',
    f"| 5 | 6 | 5 | 4 | `{COMPOSED}` | its decomposed twin: identical on screen, unequal |",
    f"| `{COMPOSED}` | decomposed | 6 | 5 |",
    f"the decomposed `{COMPOSED}` is five code points",
]

MUST_PASS = [
    f'   "{DECOMPOSED}" (decomposed)      6 bytes    5 code points    4 things a person sees',
    f"| 5 | 6 | 5 | 4 | `{DECOMPOSED}` | its decomposed twin: identical on screen, unequal |",
    "two spellings    : 'e\u0301' is c3 a9 composed or 65 cc 81 decomposed,",
    r"$ nfd=$(printf 'z\314\207o\314\201\305\202w')  # zolw, nine bytes",
    r'decomposed "cafe\u{301}" reversed -> "\u{301}efac"',
    "APFS is normalization-insensitive, so creating `\u017c\u00f3\u0142w` in NFC and again in NFD leaves one file",
    "one canonical code-point sequence (NFC, NFD \u2026) so that two spellings of `\u00e9` compare equal",
    "NFC / NFD / NFKC / NFKD: composed, decomposed, and the compatibility forms that turn `\ufb01` into `fi`",
    "Polish: which letters have a decomposed form (all of them), and a sort key after NFD",
    f"| 4 | 5 | 4 | 4 | `{COMPOSED}` | the house string \u2014 one accent |",
]


def selftest() -> int:
    wrong = []
    for line in MUST_FLAG:
        if not offending_literals(line):
            wrong.append(f"  missed:         {line.strip()[:88]}")
    for line in MUST_PASS:
        if offending_literals(line):
            wrong.append(f"  false positive: {line.strip()[:88]}")
    if wrong:
        print(f"selftest: {len(wrong)} of {len(MUST_FLAG) + len(MUST_PASS)} case(s) wrong.\n")
        print("\n".join(wrong))
        return 1
    print(
        f"selftest: {len(MUST_FLAG)} defect(s) caught, "
        f"{len(MUST_PASS)} legitimate line(s) left alone."
    )
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(scan())
