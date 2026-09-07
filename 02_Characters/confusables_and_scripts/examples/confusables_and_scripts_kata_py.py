"""Answer key: two 'a's that no normalization will ever merge.

The kata asks which of five checks separates them. Four of the five are the
checks people reach for first, and all four say the strings are fine.
"""
import unicodedata as ud

SPOOF, REAL = "paуpal", "paypal"   # SPOOF holds a Cyrillic u; they draw the same
a, b = "а", "a"

print(f"the two letters   {a!r} and {b!r}")
print(f"code points       U+{ord(a):04X} and U+{ord(b):04X}")
print(f"names             {ud.name(a)}")
print(f"                  {ud.name(b)}")
print(f"utf-8 bytes       {a.encode().hex()} and {b.encode().hex()}")
print()
print("FIVE CHECKS")
rows = [
    ("a == b", a == b),
    ("NFC equal", ud.normalize("NFC", a) == ud.normalize("NFC", b)),
    ("NFKC equal", ud.normalize("NFKC", a) == ud.normalize("NFKC", b)),
    ("casefold equal", a.casefold() == b.casefold()),
    ("same script", ud.name(a).split()[0] == ud.name(b).split()[0]),
]
for label, got in rows:
    print(f"   {label:<16} {got}")
print()
print("Every one of them says False, and only the last one says it for the")
print("right reason. The first four are asking 'are these two spellings of one")
print("character?' -- and the honest answer is no, so they cannot help. These")
print("are two DIFFERENT characters that history drew the same way, and")
print("normalization exists to merge spellings, not to merge letters.")
print()
print("What does work is a rule about the whole string:")
scripts = {s: sorted({ud.name(c).split()[0] for c in s if c.isalpha()}) for s in (SPOOF, REAL)}
for s, sc in scripts.items():
    verdict = "MIXED -- refuse it" if len(sc) > 1 else "single script"
    print(f"   {s!r:<12} scripts {sc}  {verdict}")
print()
print("That is the check: not 'is this character suspicious' but 'does this")
print("identifier mix scripts'. One letter is never wrong on its own -- Cyrillic")
print("a is the right letter in a Cyrillic word.")

assert a != b and ud.normalize("NFKC", a) != b
