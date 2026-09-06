#!/usr/bin/env python3
"""Two spellings of one word, and the four functions that reconcile them.

Every decomposed string in this file is written with escapes rather than pasted.
That is not fussiness -- section 1 is what happened when it was pasted."""

import unicodedata

N = unicodedata.normalize
FROZEN = unicodedata.ucd_3_2_0  # Unicode 3.2, sealed in 2002, identical everywhere
RULE = "-" * 72

COMPOSED = "caf\u00e9"     # c a f  e-with-acute
DECOMPOSED = "cafe\u0301"  # c a f  e  combining-acute


def cps(s):
    """A string as its code points, the way a bug report should quote it."""
    return " ".join("U+%04X" % ord(c) for c in s)


def visible(s):
    """Show a string, but spell out anything a space could be mistaken for."""
    return "".join(c if c.isprintable() and c != " " else "\\u%04x" % ord(c) for c in s)


print("1. THE LITERAL YOU CANNOT TRUST")
print(RULE)
print("   This page's whole subject is two strings that print the same. So the")
print("   two spellings CANNOT be pasted into the source as literals -- an")
print("   editor, a terminal, a paste buffer or a filesystem may quietly")
print("   normalize one of them on the way in, and then the program proves")
print("   nothing while still looking correct.")
print()
print("   Both of these were typed as 'cafe' plus an accent:")
print("     COMPOSED    = \"caf\\u00e9\"     %s" % cps(COMPOSED))
print("     DECOMPOSED  = \"cafe\\u0301\"    %s" % cps(DECOMPOSED))
print()
print("   They render as %s and %s, and: COMPOSED == DECOMPOSED -> %s"
      % (COMPOSED, DECOMPOSED, COMPOSED == DECOMPOSED))
print()

print("2. THE FOUR FORMS, ON ONE WORD")
print(RULE)
print("   form   code points  bytes  the code points themselves")
for form in ("NFC", "NFD", "NFKC", "NFKD"):
    s = N(form, DECOMPOSED)
    print("   %-6s %-12d %-6d %s" % (form, len(s), len(s.encode("utf-8")), cps(s)))
print()
print("   C is composed, D is decomposed, and the K forms are a second axis")
print("   entirely -- section 6. On a plain accented word the K forms have")
print("   nothing to do, so NFKC == NFC here: %s" % (N("NFKC", DECOMPOSED) == N("NFC", DECOMPOSED)))
print()
print("   All four are idempotent -- running one twice changes nothing:")
print("     %s" % all(N(f, N(f, DECOMPOSED)) == N(f, DECOMPOSED) for f in ("NFC", "NFD", "NFKC", "NFKD")))
print()

print("3. NFC IS NOT 'PUT THE ACCENTS BACK ON'")
print(RULE)
print("   Two characters with no combining mark anywhere in them, which NFC")
print("   nevertheless replaces -- they are SINGLETONS, code points Unicode")
print("   encoded twice by accident of history and now folds together:")
print()
print("   code point  name           NFC gives  which is")
for cp in (0x212B, 0x2126):
    ch = chr(cp)
    out = N("NFC", ch)
    print("   %-11s %-14s %-10s %s"
          % ("U+%04X" % cp, unicodedata.name(ch), cps(out), unicodedata.name(out)))
print()
print("   So NFC can change a string that contains no accent at all. If you")
print("   are comparing an angstrom against an angstrom, this is the reason")
print("   one of them lost.")
print()

print("4. AND IT IS NOT A ROUND TRIP")
print(RULE)
print("   NFC(NFD(x)) == x looks like it must hold. It does not, for two")
print("   groups: the singletons above, and the COMPOSITION EXCLUSIONS --")
print("   characters NFD takes apart and NFC is forbidden to reassemble.")
print()
print("   code point  name                    NFD gives      round trips?")
for cp in (0x0958, 0x0F43, 0x00E9):
    ch = chr(cp)
    d = N("NFD", ch)
    print("   %-11s %-23s %-14s %s"
          % ("U+%04X" % cp, unicodedata.name(ch)[:23], cps(d), N("NFC", d) == ch))
print()
print("   The last row is a normal character, for contrast. For the first two,")
print("   NFD is a one-way door -- which is why 'normalize on the way in' means")
print("   pick ONE form and keep it, not 'convert freely in both directions'.")
print()

print("5. THE ACCENT THAT COMES OFF, AND THE ONE THAT DOES NOT")
print(RULE)
print("   A Polish word, letter by letter. Not every diacritic is a combining")
print("   mark -- a stroke through a letter is part of the letter's own shape:")
print()
print("   char  code point  name                                 NFD")
for ch in "\u017c\u00f3\u0142w":            # zolw -- Polish for turtle
    d = N("NFD", ch)
    print("   %-5s %-11s %-36s %s"
          % (ch, "U+%04X" % ord(ch), unicodedata.name(ch), cps(d)))
print()
POLISH = "\u0105\u0107\u0119\u0142\u0144\u00f3\u015b\u017a\u017c"
undecomposable = [c for c in POLISH if N("NFD", c) == c]
print("   z-with-dot and o-with-acute come apart. l-with-stroke does not, and")
print("   never will: there is no COMBINING STROKE to peel off it.")
print()
print("   Polish has %d letters with a diacritic. Exactly %d of them has no"
      % (len(POLISH), len(undecomposable)))
print("   decomposed form at all: %s. So a rule that says 'strip the combining"
      % " ".join(undecomposable))
print("   marks to get ASCII' quietly leaves one letter standing.")
print()

print("6. COMPATIBILITY IS A DIFFERENT QUESTION, AND IT IS LOSSY")
print(RULE)
print("   NFKC does everything NFC does, then also replaces characters with")
print("   whatever is 'the same, roughly'. Read the fourth column and decide")
print("   whether roughly is good enough:")
print()
print("   input     NFKC       cp   what was lost")
LOSSES = [
    ("ﬁ", "the ligature was a typographic choice"),
    ("x²", "x squared became x 2 -- the meaning, not the look"),
    ("½", "one character became three, including a slash"),
    ("１２３", "fullwidth digits, common in Japanese input"),
    ("℀", "one character became a slash -- a path separator"),
    ("\u00a0", "a NO-BREAK SPACE became an ordinary space"),
    ("．", "a FULLWIDTH FULL STOP became a plain dot"),
]
for src, note in LOSSES:
    print("   %-9s %-10s %-4d %s"
          % (visible(src), visible(N("NFKC", src)), len(N("NFKC", src)), note))
print()
print("   The last three are why NFKC belongs on a search index and a username")
print("   uniqueness check, and NOT on text you will store and hand back. Two")
print("   of them turn a harmless character into a path separator or a dot.")
print()

print("7. CASE IS A SEPARATE AXIS, AND IT MOVES FIRST")
print(RULE)
print("   Normalizing does not fold case, and folding case does not normalize.")
print()
print("   char  lower   upper   casefold  code points of casefold")
for ch in "\u00df\u1e9e\u0130\u03c2\u03c3":
    print("   %-5s %-7s %-7s %-9s %s"
          % (ch, ch.lower(), ch.upper(), ch.casefold(), cps(ch.casefold())))
print()
print("   Row 1: lower() leaves eszett alone; casefold() gives 'ss'. That is")
print("   the difference, and it is why a caseless comparison uses casefold.")
print("   Rows 4 and 5 are Greek final sigma and ordinary sigma. lower()")
print("   keeps them apart; casefold() makes them one letter, which is what")
print("   a search box wants and what == will not give you.")
print()
print("   Row 3 is the one that decides the ORDER. Casefolding a Turkish")
print("   dotted capital I emits a combining mark that was not there before:")
print()
print("     '\\u0130'.casefold()  ->  %s" % cps("\u0130".casefold()))
print()
print("   So casefold can CREATE the very thing normalization exists to")
print("   reconcile. Normalize after folding, not before:")
print()
print("     s.casefold() then NFC   -- correct")
print("     NFC then s.casefold()   -- leaves a stray combining mark")
print()
print("   Unicode's own definition of a caseless match puts an NFD on both")
print("   sides of the fold for the same reason. In practice, for a login")
print("   name or a search key:")
print()
print("     key = unicodedata.normalize('NFC', s.casefold())")
print()

print("8. THE ONE THING ON THIS PAGE YOU MAY WRITE DOWN")
print(RULE)
print("   Chapter 2 said no Unicode table lookup belongs in an answer key,")
print("   because two machines carry two tables. Normalization is the")
print("   exception, and it is an exception on purpose.")
print()
print("   Unicode's Normalization Stability Policy, in force since 4.1:")
print("   if a string holds only characters your table already knows, its")
print("   normalized form is the same under every later version, forever.")
print()
print("   Asked of the 2002 table and this one, on characters both know:")
print()
print("   char  frozen 3.2 NFD       live NFD              agree")
for ch in "\u00e9\u017c\u00c5":
    a, b = FROZEN.normalize("NFD", ch), N("NFD", ch)
    print("   %-5s %-21s %-21s %s" % (ch, cps(a), cps(b), a == b))
print()
print("   And the one place the old table is wrong -- a character it never")
print("   had, so it has no decomposition to apply and returns it untouched:")
print()
bali = "ᬆ"
print("     %s  %s" % ("U+1B06", unicodedata.name(bali)))
print("       frozen 3.2 NFD   %-18s (unchanged -- not in that table)" % cps(FROZEN.normalize("NFD", bali)))
print("       live NFD         %s" % cps(N("NFD", bali)))
print()
print("   Read the guarantee's condition again: 'only characters your table")
print("   already knows'. The stability policy is a promise about the past,")
print("   not about characters that had not been invented yet.")
