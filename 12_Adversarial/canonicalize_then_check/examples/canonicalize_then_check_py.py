#!/usr/bin/env python3
"""The check ran first, and something downstream changed the string afterwards.

Every character used here has been in Unicode since 1.1, and the normalization
stability policy guarantees its decomposition can never change -- so these
mappings are safe to hold in an answer key. A COUNT over the whole table is not;
see the exercise at the foot of the page.
"""

import unicodedata as ud

BLOCKED = ("<", ">", "/", "\\", "..")


def gate(s: str) -> bool:
    """The check. Reject anything containing a character we consider dangerous."""
    return not any(bad in s for bad in BLOCKED)


def named(s: str) -> str:
    return " + ".join(ud.name(c, f"U+{ord(c):04X}") for c in s)


payloads = [
    ("＜script＞", "a tag"),
    ("．．／．．／etc／passwd", "a path"),
    ("℀", "one character, three after"),
]

print("1. THE GATE SAYS YES")
for s, what in payloads:
    print(f"   {what:<28} gate(...) = {gate(s)}")
print(f"   blocked substrings: {' '.join(repr(b) for b in BLOCKED)}")
print("   None of these strings contains any of them. The gate is not broken,")
print("   not bypassed, and not misconfigured. It is answering correctly.")
print()

print("2. AND THEN SOMETHING NORMALISES")
for s, what in payloads:
    after = ud.normalize("NFKC", s)
    print(f"   {what:<28} {s}")
    print(f"   {'':<28}   -> NFKC -> {after!r}")
    print(f"   {'':<28}   gate would now say: {gate(after)}")
print("   Nobody attacked the gate. A later stage -- a database column with a")
print("   normalising collation, a JSON library, a filename lookup, a template")
print("   engine -- did the one thing everybody agrees is correct hygiene, and")
print("   manufactured the exact characters the gate exists to reject.")
print()
print("   The third one is worth staring at. It is a SINGLE code point:")
print(f"     {payloads[2][0]}  U+2100  {named(payloads[2][0])}")
print("   NFKC expands it to three characters, one of which is a path separator.")
print("   No filter that scans for '/' can see a slash that does not exist yet.")
print()

print("3. THE SAME TWO STEPS, SWAPPED")
print("   def safe(s): return gate(unicodedata.normalize('NFKC', s))")
for s, what in payloads:
    print(f"   {what:<28} safe(...) = {gate(ud.normalize('NFKC', s))}")
print("   Same gate, same strings, same normalisation. Only the order changed.")
print("   Canonicalise, then check, then STORE THE CANONICAL FORM -- so nothing")
print("   downstream is ever handed the spelling you did not check.")
print()

print("4. TWO THAT NFKC DOES NOT TOUCH")
for cp in (0x2215, 0x2044):
    c = chr(cp)
    print(f"   U+{cp:04X}  {c}  {ud.name(c)}")
    print(f"           NFKC -> {ud.normalize('NFKC', c)!r}   (unchanged)")
print("   They look like a slash and Unicode says they are not one, so")
print("   normalising is not a defence against them either. What turns THESE")
print("   into '/' is a different kind of table: a 'best fit' mapping, which")
print("   substitutes a similar-looking character when a target encoding has")
print("   no exact match. That conversion happens below the application, and")
print("   the page has the story.")
print()

print("5. THE RULE, IN ONE LINE")
print("   Any transformation that runs AFTER your check is part of your")
print("   attack surface, and normalisation is a transformation.")
print("   Decode once, canonicalise once, check the canonical form, and pass")
print("   the canonical form on. Three verbs, one order, no second spelling.")
