#!/usr/bin/env python3
"""RFC 3454 stringprep: the step that runs BEFORE anything is encoded.

Encoding asks "which bytes write this string". Preparation asks the harder
question underneath it: "are these two strings the same name". Map, normalize,
prohibit, check bidi -- four steps, in that order, and a profile either returns
a string or returns an error, never both.

Every stringprep step this program runs reads the table frozen at Unicode 3.2,
sealed in 2002 -- except one, and section 9 is about it. Python's frozen table
has no case data, so the case fold (table B.2) also reads the LIVE table, and in
every CPython release before a 2026 fix that leaked into its answers: U+1E9E
folded to 'ss' while table A.1, in the same module, called it unassigned. So
this program prints no fold of a character the RFC leaves alone, and every line
below is the same on every machine, before that fix and after it. That is the
whole reason the page may print them.

Run:  python3 preparing_a_string_py.py
"""

import stringprep
import unicodedata

BAR = "-" * 72


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


# The prohibition tables a profile picks from. Names are the RFC's section
# numbers, so a refusal below can be looked up in the document itself.
PROHIBITED = [
    ("C.1.2 non-ASCII space", stringprep.in_table_c12),
    ("C.2.1 ASCII control", stringprep.in_table_c21),
    ("C.2.2 non-ASCII control", stringprep.in_table_c22),
    ("C.3 private use", stringprep.in_table_c3),
    ("C.4 noncharacter", stringprep.in_table_c4),
    ("C.5 surrogate", stringprep.in_table_c5),
    ("C.6 inappropriate for plain text", stringprep.in_table_c6),
    ("C.7 inappropriate as canonical", stringprep.in_table_c7),
    ("C.8 changes display / deprecated", stringprep.in_table_c8),
    ("C.9 tagging", stringprep.in_table_c9),
]


def prepare(s, *, fold=True, check_bidi=True):
    """A minimal stringprep profile -- the whole RFC in four steps."""
    # 1. MAP -- delete what table B.1 says is invisible, fold case with B.2.
    #    Mapped characters are NOT re-scanned; this is one pass, on purpose.
    mapped = []
    for ch in s:
        if stringprep.in_table_b1(ch):
            continue
        mapped.append(stringprep.map_table_b2(ch) if fold else ch)
    s = "".join(mapped)

    # 2. NORMALIZE -- the profile chooses; nameprep chose NFKC. The RFC pins it
    #    to Unicode 3.2 like everything else, so it is the frozen table's NFKC --
    #    the one the stdlib's own nameprep calls -- not the live one.
    s = unicodedata.ucd_3_2_0.normalize("NFKC", s)

    # 3. PROHIBIT -- any hit is an error, and an error means no string at all.
    for ch in s:
        for why, in_table in PROHIBITED:
            if in_table(ch):
                raise ValueError(f"U+{ord(ch):04X} prohibited by {why}")

    # 4. CHECK BIDI -- RFC 3454 section 6, requirements 2 and 3.
    if check_bidi and s and any(stringprep.in_table_d1(c) for c in s):
        if any(stringprep.in_table_d2(c) for c in s):
            raise ValueError("bidi: an R/AL string may hold no L character")
        if not (stringprep.in_table_d1(s[0]) and stringprep.in_table_d1(s[-1])):
            raise ValueError("bidi: an R/AL string must begin and end with R/AL")
    return s


def show(label, s):
    try:
        out = prepare(s)
        print(f"   {label:<26} {s!r:<26} -> {out!r}")
    except ValueError as exc:
        print(f"   {label:<26} {s!r:<26} -> error: {exc}")


# ------------------------------------------------------------------ 1
head(1, "THE TABLES OF A 2002 RFC, SHIPPED IN YOUR PYTHON")
print("   import stringprep")
print()
print(f"   membership tests it exposes   {len([n for n in dir(stringprep) if n.startswith('in_table')])}")
print("   mapping tables                2   (map_table_b2, map_table_b3)")
print()
print("   Every one is an appendix of RFC 3454 turned into a function, and the")
print("   module opens by pinning the table it reads them from:")
print()
print("       from unicodedata import ucd_3_2_0 as unicodedata")
print("       assert unicodedata.unidata_version == '3.2.0'")
print()
print("   (A 2026 fix renames the alias unicodedata_320 and adds a second")
print("   assert -- on the LIVE table. Section 9 is why it needs one.)")
print()
print("   So this is the frozen table from `The table has a version`, with a")
print("   protocol built on top of it -- for every table but one: the case")
print("   fold reads the live table too. Everything printed below is the same")
print("   on every machine, before that fix and after it.")

# ------------------------------------------------------------------ 2
head(2, "FOUR STEPS, AND THE ORDER IS NORMATIVE")
print("   map -> normalize -> prohibit -> check bidi")
print()
for label, s in (
    ("plain", "Cafe"),
    ("composed", "caf\u00e9"),
    ("decomposed", unicodedata.normalize("NFD", "caf\u00e9")),
    ("case folded", "CAF\u00c9"),
):
    print(f"   {label:<14} {len(s)} code points  {s!r:<20} -> {prepare(s)!r}")
print()
print("   Four spellings, one prepared string. That is the entire purpose:")
print("   two people who think they typed the same name now have.")
print()
print("   Rows 2 and 3 are the same picture on screen, five code points")
print("   against six, and the decomposed one is BUILT here rather than")
print("   typed, because a decomposed string cannot be typed. NFKC is what")
print("   reconciles them; preparation without it would keep them apart.")

# ------------------------------------------------------------------ 3
head(3, "MAPPED TO NOTHING: THE CHARACTERS THAT SIMPLY VANISH")
print("   Table B.1 is deleted before anything else happens, because whether")
print("   these are present or absent must not make two names different.")
print()
for ch, name in (
    ("­", "SOFT HYPHEN"),
    ("​", "ZERO WIDTH SPACE"),
    ("‍", "ZERO WIDTH JOINER"),
    ("﻿", "ZWNBSP -- the BOM, mid-string"),
    ("͏", "COMBINING GRAPHEME JOINER"),
    ("️", "VARIATION SELECTOR-16"),
):
    tables = [t for t in ("b1", "c12", "c22") if getattr(stringprep, "in_table_" + t)(ch)]
    print(f"   U+{ord(ch):04X}  {name:<30} in tables {tables}")
print()
print("   U+FEFF is in two of them at once, which is not a contradiction: B.1")
print("   deletes it, C.2.2 would reject it, and a profile says which of the")
print("   two it applies. Nameprep deletes.")
print()
family = "\U0001f469‍\U0001f469‍\U0001f467"
print(f"   the cast's ZWJ family      {family!r}")
print(f"                              {len(family)} code points")
print(f"   after step 1               {prepare(family)!r}")
print(f"                              {len(prepare(family))} code points")
print()
print("   The joiners are gone, so one family became three people. Deleting")
print("   an invisible character is the right call for a login name and the")
print("   wrong one for text a human will read back. A profile is a choice.")

# ------------------------------------------------------------------ 4
head(4, "FOLDING THAT CHANGES THE LENGTH")
for ch in ("ß", "İ", "Ω"):
    folded = stringprep.map_table_b2(ch)
    print(f"   U+{ord(ch):04X}  {ch}  {unicodedata.name(ch):<38} -> {folded!r}  ({len(folded)})")
print()
print("   Sharp s folds to two characters -- so a name gets LONGER during a")
print("   step whose job was to make it comparable. A profile must expect")
print("   that; RFC 3454 says so in as many words. U+0130 does it with a")
print("   combining mark instead.")
print()
print("   The capital, U+1E9E, is missing on purpose. It is younger than the")
print("   RFC, and what this module folds it to depends on which release of")
print("   Python you run -- section 9.")
print()
print("   B.2 is upper-to-lower, chosen because Internet protocols had a")
print("   tradition of lowercase. The RFC built it by iterating to a fixed")
print("   point, which is worth reading as pseudocode because it is four")
print("   lines and it invented what Unicode later called NFKC_Casefold:")
print()
print("       b = NormalizeWithKC(Fold(a))")
print("       c = NormalizeWithKC(Fold(b))")
print("       if c is not the same as b, add a mapping for a -> c")
print()
print("   Fold once and normalizing can undo it; fold and normalize until")
print("   nothing moves, and the table is stable from that point on.")

# ------------------------------------------------------------------ 5
head(5, "THE SAME NAME, PREPARED TWO WAYS, IS TWO DIFFERENT DOMAINS")
for host in ("faß.de", "STRASSE.de", "Bücher.de", "ExAmPlE.com"):
    print(f"   {host!r:<16} .encode('idna')  ->  {host.encode('idna')!r}")
print()
print("   Row 1 is the whole argument. Nameprep is a stringprep profile, and")
print("   its B.2 folds sharp s to 'ss' -- so the prepared label is pure")
print("   ASCII, punycode never runs, and the string a German typed resolves")
print("   to a name they did not type. IDNA2008 abolished the mapping step")
print("   and keeps the character, giving a DIFFERENT registrable domain from")
print("   the same keystrokes. Both are correct implementations of a standard.")
print()
print("   Row 4 is the quieter trap. An all-ASCII label skips preparation")
print("   entirely (RFC 3490 section 4.1), so the case survives -- while row 3")
print("   was folded on its way through. One function, two contracts, chosen")
print("   by a character you did not type.")

# ------------------------------------------------------------------ 6
head(6, "PROHIBITION IS A DESIGN TOOL, NOT AN ERROR PATH")
for probe, label in (
    ("ad" + chr(0x202E) + "min", "RIGHT-TO-LEFT OVERRIDE"),
    ("ad" + chr(0xE000) + "min", "a private-use character"),
    ("ad" + chr(0xFFFE) + "min", "a permanent noncharacter"),
    ("ad" + chr(0xE0041) + "min", "a tagging character"),
):
    show(label, probe)
print()
print("   Nine categories of refusal, and not one of them is about a")
print("   character being WRONG. They are characters whose presence in an")
print("   identifier nobody can verify by looking. U+202E is the one that")
print("   reverses the display of everything after it -- the Trojan Source")
print("   class of bug, published in 2021 and prohibited by number here in")
print("   December 2002.")
print()
print("   And two that are NOT refused, which is the more useful half:")
print()
show("NO-BREAK SPACE", "ad" + chr(0xA0) + "min")
show("ACCOUNT OF", "\u2100")
print()
print(f"   ...yet in_table_c12(NO-BREAK SPACE) is {stringprep.in_table_c12(chr(0xA0))}, and C.1.2 is")
print("   `prohibit non-ASCII space`. It got through because step 2 had")
print("   already turned it into an ordinary space and step 3 never saw it.")
print("   That is what `the order is normative` buys, and it is why a")
print("   profile may not reorder the steps for convenience.")
print()
print("   U+2100 goes the other way: nothing prohibits it, and NFKC expands")
print("   it into three characters, one of which is a PATH SEPARATOR.")
print("   Preparation does not only filter -- it rewrites, and what it")
print("   writes has to be safe in whatever consumes the prepared string.")


# ------------------------------------------------------------------ 7
head(7, "BIDI IS A RULE ABOUT SHAPE, NOT ABOUT RENDERING")
for s, label in (
    ("ا1", "aleph then 1"),
    ("ا1ب", "aleph, 1, beh"),
    ("اb", "aleph then a latin b"),
):
    show(label, s)
print()
print("   The RFC's own two examples, and they are checkable arithmetic: a")
print("   string holding any R/AL character may hold no L character, and must")
print("   begin and end with R/AL. No font, no layout engine, no rendering --")
print("   just membership in tables D.1 and D.2. Latin digits are in neither,")
print("   which is why 'aleph 1 beh' passes and 'aleph 1' does not.")

# ------------------------------------------------------------------ 8
head(8, "THE PIN THAT PROTECTS YOU IS THE PIN THAT LOCKS YOU OUT")
print("   Table A.1 is 'unassigned in Unicode 3.2', and the module computes")
print("   it the only way a frozen table can:")
print()
print("       def in_table_a1(code):")
print("           if unicodedata.category(code) != 'Cn': return False")
print()
for ch, what in (
    ("\U0001f600", "GRINNING FACE, assigned 2012"),
    ("ẞ", "CAPITAL SHARP S, assigned 2008"),
    ("\U00011db0", "TOLONG SIKI LETTER I, assigned 2025"),
    ("͸", "genuinely unassigned, still is"),
):
    print(f"   U+{ord(ch):04X}  in_table_a1 -> {str(stringprep.in_table_a1(ch)):<5}  {what}")
print()
print("   Four different truths, one answer -- the identical failure `The")
print("   table has a version` found in `Cn`, except that here a standard is")
print("   built on top of it. Section 7 had to legislate around it:")
print()
print("      a STORED string  (a registered name)  MUST reject table A.1")
print("      a QUERY string   (what a user typed)  MAY allow it")
print()
print("   Read that as the trade it is. Pinning Unicode 3.2 means a domain")
print("   can never change meaning because the standard grew -- and it means")
print("   an implementation that obeys the pin refuses every character")
print("   invented after 2002, permanently, including the one above that")
print("   somebody writes their language in.")

# ------------------------------------------------------------------ 9
head(9, "THE ONE STEP THE PIN DID NOT REACH")
capital = "\u1e9e"  # LATIN CAPITAL LETTER SHARP S, assigned in Unicode 5.1 (2008)
print("   U+1E9E LATIN CAPITAL LETTER SHARP S, asked of both tables this")
print("   module can reach:")
print()
for table, call, answer, meaning in (
    ("the frozen 2002 table", "in_table_a1('\u1e9e')", str(stringprep.in_table_a1(capital)), "unassigned"),
    ("the live table", "'\u1e9e'.lower()", repr(capital.lower()), "a capital with a lowercase"),
):
    print(f"      {table:<22} {call:<17} {answer:<6} {meaning}")
print()
print("   Both are right about the table they read: the letter was added in")
print("   2008. The case fold has to side with one of them, and B.2 is built")
print("   on this function, unchanged in every Python 3:")
print()
print("       def map_table_b3(code):")
print("           r = b3_exceptions.get(ord(code))")
print("           if r is not None: return r")
print("           return code.lower()")
print()
print("   The dict is frozen into the module when it is generated; lower() is")
print("   the live table. Python's frozen table has no case mappings at all,")
print("   so the dict has to carry every row where the RFC's answer is not")
print("   today's -- and until 2026 it did not. It held only rows the RFC")
print("   writes down, the ones where RFC and lower() disagree, so a character")
print("   the RFC never mentions fell through to lower(), and U+1E9E folded")
print("   to 'ss': a fold for a letter the same module calls unassigned.")
print("   RFC 3454's own B.2 is a fixed list of 1,371 rows, and not one of")
print("   them is U+1E9E.")
print()
print("   CPython fixed it in 2026 (gh-155292). The dict now also holds an")
print("   identity row for every character the RFC leaves alone that lower()")
print("   would change -- computed against the live table, which is why the")
print("   regenerated module asserts that table's version too -- and the same")
print("   call returns '\u1e9e', the RFC's answer. Which one you get depends on")
print("   your interpreter's release, so this program prints neither. Ask")
print("   yours:")
print()
print("     python3 -c \"import stringprep; print(stringprep.map_table_b2('\\u1e9e'))\"")
print()
print("   That is section 8's trap from the other side. A frozen table cannot")
print("   tell `not invented yet` from `never will be`; a module that asks a")
print("   frozen table one question and a live one the next gives both")
print("   answers at once, and nothing it returns says which table it came")
print("   from.")
print()
print("   One answer above does come from the live table, and is printed on")
print("   purpose: 'ẞ'.lower(). U+1E9E has lowercased to U+00DF in every")
print("   Unicode that has it, from 5.1 in 2008, and Python 3.0 shipped 5.1,")
print("   so no Python 3 says anything else. Nothing in Unicode's stability")
print("   policy promises it: ẞ and ß are not a case pair, because ß")
print("   uppercases to 'SS'. So it is a bet, and this is it, made out loud.")
