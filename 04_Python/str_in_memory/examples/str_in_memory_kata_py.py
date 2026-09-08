#!/usr/bin/env python3
"""Answers for the str-in-memory kata.

Same discipline as the lesson's own example: shapes, never byte totals. Every
question below is answered with a stride, a count, a comparison or a True.

Run:  python3 str_in_memory_kata_py.py
"""

import codecs
import sys


def stride(ch):
    return sys.getsizeof(ch * 101) - sys.getsizeof(ch * 100)


def grew(make, use):
    """Does sys.getsizeof go up when an UNCHANGED string is passed to `use`?"""
    s = make()
    before = sys.getsizeof(s)
    try:
        use(s)
    except Exception:
        pass
    return sys.getsizeof(s) > before


BASE = "A" * 10

print("THREE WAYS TO MAKE ONE STRING WIDER")
print("   %-10s %-8s %-8s %-10s %s"
      % ("appended", "stride", "len +", "buffer", "grew by more than 1 byte"))
for ch, cp in (("é", "U+00E9"), ("ż", "U+017C"), ("\U0001f600", "U+1F600")):
    grown = BASE + ch
    print("   %-10s %-8d %-8d %-10s %s"
          % (cp, stride(ch), len(grown) - len(BASE),
             {1: "latin-1", 2: "UCS-2", 4: "UCS-4"}[stride(ch)],
             sys.getsizeof(grown) - sys.getsizeof(BASE) > 1))

print()
print("   len() goes up by exactly one every time -- one character is one")
print("   character, whatever it costs. The BUFFER goes up by more than one")
print("   byte in all three rows, and for two different reasons: the e-acute")
print("   keeps the one-byte stride but forces the bigger object header,")
print("   while the other two change the stride for all eleven characters.")
print()

print("WHICH CALLS CAN MOVE getsizeof ON AN UNCHANGED STRING")
CALLS = [
    ("s.encode('utf-8')", lambda s: s.encode("utf-8")),
    ("codecs.lookup(s)", lambda s: codecs.lookup(s)),
    ("sys.intern(s)", lambda s: sys.intern(s)),
    ("s.upper()", lambda s: s.upper()),
]
print("   %-22s %-14s %s" % ("call", "on 100 x 'é'", "on 100 x 'A'"))
for label, fn in CALLS:
    print("   %-22s %-14s %s"
          % (label,
             grew(lambda: "".join(["é"] * 100), fn),
             grew(lambda: "".join(["A"] * 100), fn)))
print()
print("   Only codecs.lookup() moves it, and only in the first column.")
print()
print("   The reason is not that the other three are cheap. encode() and")
print("   upper() both build a NEW object and leave the original alone;")
print("   intern() returns a different reference to an equal string without")
print("   attaching anything. codecs.lookup() is the odd one out because it")
print("   takes its argument as a C string, and that conversion caches the")
print("   UTF-8 form on the str itself.")
print()

print("THE PROPERTY THAT MAKES A STRING IMMUNE")
ascii_only = "".join(["A"] * 100)
latin1 = "".join(["é"] * 100)
print("   %-34s %s" % ("all characters below U+0080:", max(ascii_only) < "\x80"))
print("   %-34s %s" % ("  its utf-8 form is its buffer:",
                       len(ascii_only.encode("utf-8")) == len(ascii_only)))
print("   %-34s %s" % ("  so there is nothing to cache:",
                       not grew(lambda: "".join(["A"] * 100),
                                lambda s: codecs.lookup(s))))
print()
print("   %-34s %s" % ("all characters below U+0100:", max(latin1) < "Ā"))
print("   %-34s %s" % ("  but its utf-8 form is longer:",
                       len(latin1.encode("utf-8")) > len(latin1)))
print("   %-34s %s" % ("  so a cache is a second copy:",
                       grew(lambda: "".join(["é"] * 100),
                            lambda s: codecs.lookup(s))))
print()
print("   Being ASCII is the property -- not being narrow. A Latin-1 string")
print("   has the same one-byte stride and is NOT immune, because one byte")
print("   per character in the buffer is two bytes per character in UTF-8.")
