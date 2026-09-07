#!/usr/bin/env python3
"""Source code that renders as one program and compiles as another.

This file contains no bidi control character and no confusable identifier as a
raw character -- every one is written as an escape. That is deliberate, and it
is the same rule the page recommends: an escape is visible in a diff, findable
by grep, and cannot rearrange the file it lives in.
"""

import unicodedata as ud

CY_A = "\u0430"  # CYRILLIC SMALL LETTER A -- looks exactly like ASCII 'a'

# Two definitions. On screen the names are the same eight characters.
SRC = (
    "def is_admin(user):\n"
    "    return user == 'root'\n"
    f"def is_{CY_A}dmin(user):\n"
    "    return True\n"
)

print("1. TWO FUNCTIONS, ONE APPEARANCE")
ns: dict = {}
exec(compile(SRC, "<review>", "exec"), ns)
defined = sorted(k for k in ns if k.endswith("dmin"))
for name in defined:
    print(f"   defined: {name!r}")
    print(f"            {' '.join(f'U+{ord(c):04X}' for c in name)}")
print(f"   same name?   {defined[0] == defined[1]}")
print(f"   is_admin('nobody')  -> {ns['is_admin']('nobody')}")
print(f"   is_{CY_A}dmin('nobody')  -> {ns['is_' + CY_A + 'dmin']('nobody')}")
print("   One of those is a backdoor. Both lines above are eight characters")
print("   long and, in every font, identical. A reviewer has nothing to see.")
print("   Note the code points: only ONE character differs, at position four.")
print()

print("2. AND PYTHON SAYS NOTHING")
with_rlo = "x = 1  # \u202e ereh gnihton\nresult = x + 1\n"
ns2: dict = {}
try:
    exec(compile(with_rlo, "<review>", "exec"), ns2)
    raised = "no"
except Exception as e:  # never taken -- the point is that it is not
    raised = type(e).__name__
print(f"   source contains U+202E?  {chr(0x202E) in with_rlo}")
print(f"   compile() raised?        {raised}")
print(f"   result                   {ns2['result']}")
print("   No error, no warning, not even under -W error. CPython's tokenizer")
print("   has no opinion about text direction, because text direction is not")
print("   a property of the program -- only of the screen the program is")
print("   being read on. That gap is the whole of Trojan Source.")
print()

print("3. WHAT THIS PROGRAM REFUSES TO PRINT")
BIDI = [0x202A, 0x202B, 0x202C, 0x202D, 0x202E, 0x2066, 0x2067, 0x2068, 0x2069]
for cp in BIDI:
    c = chr(cp)
    print(f"   U+{cp:04X}  {ud.bidirectional(c):<3}  {ud.name(c)}")
print("   Nine characters, none of them printed above as itself -- because an")
print("   answer key holding a raw override would reorder the page that shows")
print("   it, and this library's answer keys are read by people. Escapes only.")
print()

print("4. THE DETECTOR IS TEN LINES")


def suspicious(src: str) -> list[str]:
    hits = []
    for lineno, line in enumerate(src.splitlines(), 1):
        for col, ch in enumerate(line, 1):
            if ord(ch) in BIDI:
                hits.append(f"line {lineno} col {col}: {ud.name(ch)}")
            elif ord(ch) > 0x7F and ch.isalpha():
                hits.append(f"line {lineno} col {col}: non-ASCII letter {ud.name(ch)}")
    return hits


for label, src in (("the two definitions", SRC), ("the comment", with_rlo)):
    print(f"   {label}:")
    for hit in suspicious(src) or ["   clean"]:
        print(f"     {hit}")
print("   That is the whole defence, and it belongs in CI rather than in a")
print("   reviewer's eyes: a rule a person cannot apply is not a control.")
print()

print("5. THE RULE")
print("   Two readers, again -- but this time one of them is a human being.")
print("     the compiler reads code points, in order, and has no screen")
print("     the reviewer reads a rendering, which reorders and which draws")
print("       two different code points with the same picture")
print("   So: forbid the nine controls outright in source, require identifiers")
print("   to be ASCII (or a single script), and render anything from outside")
print("   with escapes rather than glyphs. Rust does the first by default and")
print("   warns on the second; Python does neither, and both are lint rules")
print("   somebody has to switch on.")
