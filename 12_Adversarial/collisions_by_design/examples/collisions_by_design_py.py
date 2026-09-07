#!/usr/bin/env python3
"""Any identity function that is not injective hands one account to two people.

Every mapping below is a case mapping or a compatibility decomposition of a
character assigned in Unicode 1.1 or 3.0; the stability policy fixes both, so
these results are safe to record. A COUNT over the whole table is not.
"""

import unicodedata as ud


def cps(s: str) -> str:
    return " ".join(f"U+{ord(c):04X}" for c in s)


print("1. TWO ADDRESSES, ONE UPPERCASE")
victim = "mike@example.org"
attacker = "mıke@example.org"  # U+0131 LATIN SMALL LETTER DOTLESS I
print(f"   victim     {victim!r}")
print(f"              {cps(victim[:4])} ...")
print(f"   attacker   {attacker!r}")
print(f"              {cps(attacker[:4])} ...")
print(f"   equal?     {victim == attacker}")
print(f"   uppercased {victim.upper()!r}")
print(f"              {attacker.upper()!r}")
print(f"   equal now? {victim.upper() == attacker.upper()}")
print("   Register the second address; ask for a password reset; the lookup is")
print("   case-insensitive, so it finds the first account -- and the mail goes")
print("   to whichever address the code decided to send to. If that is the one")
print("   that was submitted rather than the one that was stored, the token")
print("   leaves the building. That is CVE-2019-19844, in four lines.")
print()

print("2. THE FOLD IS NOT A ROUND TRIP")
print(f"   {'char':<8} {'upper':<8} {'lower(upper)':<14} {'back to start?'}")
for s in ("ß", "ı", "İ", "ﬁ", "ẞ"):
    trip = s.upper().lower()
    print(f"   {s:<8} {s.upper():<8} {trip:<14} {trip == s}")
print("   Not one of them survives the journey. Case mapping is not a bijection")
print("   -- it merges characters on the way up and cannot un-merge them coming")
print("   back -- so it cannot be an identity function. It can only be a way of")
print("   choosing which distinct strings you are willing to call the same.")
print()

print("3. 'CASE-INSENSITIVE' IS NOT ONE RELATION")
pairs = [
    ("ß", "ss"),
    ("ı", "i"),
    ("İ", "i"),
    ("ﬁ", "fi"),
    ("K", "k"),
]
folds = {
    "lower": str.lower,
    "upper": str.upper,
    "casefold": str.casefold,
    "NFKC+fold": lambda s: ud.normalize("NFKC", s).casefold(),
}
print(f"   {'pair':<22} " + " ".join(f"{n:>10}" for n in folds))
for a, b in pairs:
    cells = " ".join(f"{('SAME' if f(a) == f(b) else '-'):>10}" for f in folds.values())
    print(f"   {a + '  vs  ' + b:<22} {cells}")
print("   Read the rows, not the columns. Every row is one pair of strings, and")
print("   four systems that all describe themselves as case-insensitive give")
print("   four different answers about whether it is one user or two.")
print("   The dotless i is the sharpest: only the uppercase fold merges it,")
print("   which is why the bug in section 1 needed a system that uppercases.")
print()

print("4. A STRONGER FOLD MAKES BIGGER CLASSES")
name = "ᴮᶦᵍᴮᶦʳᵈ"
print(f"   registered   {name!r}")
print(f"                {cps(name)}")
print(f"   NFKC         {ud.normalize('NFKC', name)!r}")
print(f"   NFKC+fold    {ud.normalize('NFKC', name).casefold()!r}")
print("   Modifier letters are compatibility-equivalent to the letters they are")
print("   shrunken copies of, so a fold that includes NFKC pulls them back into")
print("   the alphabet. Spotify hit this in 2013 with a canonicaliser stronger")
print("   than NFKC -- strong enough to reach plain 'bigbird' -- and the")
print("   canonicalisation was the DEFENCE against impersonation. It worked; it")
print("   just also merged an account nobody meant to merge.")
print()

print("5. SO THE FIX IS NOT A BETTER FOLD")
print("   There is no injective fold. Every one of them defines equivalence")
print("   classes, and the only question is which classes you want.")
print("   What actually works is to treat the class as the thing being")
print("   registered:")
print("     canonical = fold(input)          # one fold, named, everywhere")
print("     if taken(canonical): reject      # the CLASS is unique, not the string")
print("     store(canonical, display=input)  # keep the original only to show")
print("     mail_to(stored_address)          # never to the address just typed")
print("   The last line is the one that turns a collision into a takeover.")
