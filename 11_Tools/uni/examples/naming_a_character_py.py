#!/usr/bin/env python3
"""The columns `uni` prints, from the standard library.

`uni` is not on either CI runner, so the sessions on this page are dated rather
than recorded. This program prints the same five columns for the same characters
using nothing but `unicodedata` and `html.entities`, which is both the check on
the page and the answer for a machine you cannot install anything on.

Only long-established characters appear here on purpose. A name or a property
that changed in a recent Unicode revision would make this program's output
depend on which Python built the runner — the one kind of drift no local run
can see. Everything below has had the same name since the 1990s.
"""

import unicodedata
from html.entities import codepoint2name

SAMPLE = "Aéż€ß"
HEADER = f"   {'char':<6} {'code point':<11} {'dec':>6}  {'utf-8':<12} {'html':<10} name"


def row(ch: str) -> str:
    cp = ord(ch)
    entity = codepoint2name.get(cp)
    html = f"&{entity};" if entity else f"&#x{cp:x};"
    return (
        f"   {ch:<6} U+{cp:04X}{'':<5} {cp:>6}  "
        f"{ch.encode('utf-8').hex(' '):<12} {html:<10} {unicodedata.name(ch)}"
    )


print("1. EVERY COLUMN uni PRINTS, FROM unicodedata")
print(HEADER)
for ch in SAMPLE:
    print(row(ch))
print("   The utf-8 column is what `xxd -p` gives you. The other four are the")
print("   ones no dump tool has, and the last one — the NAME — is the answer to")
print("   'what is this character?', which is a different question from 'how is")
print("   it stored?' and has a different answer for every character above A.")
print("   One column is not identical to uni's: ż comes out as the numeric")
print("   &#x17c; here and as &zdot; there, because html.entities carries the")
print("   HTML 4 set and uni carries HTML 5's. Both render the same character.")

print()
print("2. THE COLUMN THAT SETTLES AN NFC/NFD ARGUMENT")
for label, text in [("NFC  ", "é"), ("NFD  ", "é")]:
    print(f"   {label} {text!r}   {len(text)} code point(s), "
          f"{len(text.encode('utf-8'))} bytes")
    for ch in text:
        print(f"        U+{ord(ch):04X}  {unicodedata.name(ch)}")
print("   One é and one é. Reading the names is how you find out which one is")
print("   in front of you, and it is the fastest end to the argument about why")
print("   a filename or a search 'does not match' when it plainly should.")

print()
print("3. GOING THE OTHER WAY: FROM A NAME TO A CHARACTER")
for name in ["EURO SIGN", "LATIN SMALL LETTER Z WITH DOT ABOVE", "NO-BREAK SPACE"]:
    ch = unicodedata.lookup(name)
    print(f"   {name:<38} -> {ch!r}  U+{ord(ch):04X}  {ch.encode('utf-8').hex(' ')}")
print("   unicodedata.lookup() needs the name EXACTLY, which is the difference")
print("   from `uni search`: uni does a substring search over the whole database")
print("   and Python has no index to do that with. The standard library answers")
print("   'what is this?'; the tool also answers 'what was it called again?'.")

print()
print("4. THE PROPERTIES BEHIND THE OTHER TOOLS' BEHAVIOUR")
print(f"   {'char':<6} {'category':<10} {'combining':>9}  {'bidi':<5} numeric")
for ch in "Aé́€5":
    num = unicodedata.numeric(ch, None)
    # A combining mark has nothing to sit on here, so give it a dotted circle
    # to sit on — which is exactly what uni's ◌ is for, and why it has a -r
    # flag to turn it off.
    shown = ("◌" + ch) if unicodedata.combining(ch) else ch
    print(f"   {shown:<6} {unicodedata.category(ch):<10} "
          f"{unicodedata.combining(ch):>9}  {unicodedata.bidirectional(ch):<5} "
          f"{'-' if num is None else num}")
print("   'Mn' is a non-spacing mark — the combining acute — and its combining")
print("   class of 230 is why it draws on top of the previous letter instead of")
print("   beside it. That single row is why 'e' + U+0301 takes one column on")
print("   screen and two positions in every string type in this library.")
