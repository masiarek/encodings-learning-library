"""Answer key: five pairs, and which checks reach them.

None of the five is in the page's own table, so the kata cannot be answered by
looking one row up. Two of them are merged by casefold() and only one of those
two is about letter case, which is the point.
"""
import unicodedata as ud

PAIRS = [
    ("\u1e9b\u0323", "\u1e69",
     "long s with dot above, plus a dot below, against s with both dots"),
    ("\u0130", "i\u0307",
     "capital I with dot above, against i plus a combining dot"),
    ("\u01c4", "D\u017d",
     "the DZ-with-caron digraph, against the two letters"),
    ("\xb5", "\u03bc",
     "MICRO SIGN, against GREEK SMALL LETTER MU"),
    ("\ufeffdata", "data",
     "a BOM in front of an ASCII word"),
]

CHECKS = [
    ("NFC", lambda a, b: ud.normalize("NFC", a) == ud.normalize("NFC", b)),
    ("NFKC", lambda a, b: ud.normalize("NFKC", a) == ud.normalize("NFKC", b)),
    ("cf", lambda a, b: a.casefold() == b.casefold()),
    ("NFKC+cf", lambda a, b: ud.normalize("NFKC", ud.normalize("NFKC", a).casefold())
     == ud.normalize("NFKC", ud.normalize("NFKC", b).casefold())),
]

print(f"   {'left':<18} {'right':<14}" + "".join(f"{n:>9}" for n, _ in CHECKS))
for left, right, _ in PAIRS:
    row = "".join(f"{('=' if check(left, right) else '-'):>9}" for _, check in CHECKS)
    print(f"   {ascii(left):<18} {ascii(right):<14}{row}")
print()
for i, (left, right, note) in enumerate(PAIRS, 1):
    print(f"   {i}. {note}")
print()
print("   1 is the example UAX #15 uses to show that NFC is not 'the composed")
print("      one'. Composing cannot help here -- there is no single character")
print("      for a long s with both dots -- so NFC leaves the pair alone and")
print("      the COMPATIBILITY form, which is allowed to replace the long s")
print("      with an ordinary one, is the first thing that merges them.")
print()
print("   2 is merged by casefold() and by nothing before it. The capital I")
print("      with dot above has no canonical decomposition, so no amount of")
print("      normalizing produces 'i' plus a mark -- but its case mapping")
print("      does exactly that, which is a case question wearing a")
print("      normalization costume.")
print()
print("   3 is a digraph with a compatibility decomposition, so NFKC splits")
print("      it into two letters. Note what that costs: the string got")
print("      LONGER, and a field with room for one character now holds two.")
print()
print("   4 is the trap. casefold() merges MICRO SIGN onto Greek mu, and")
print("      there is no case anywhere in that pair -- both are lower case")
print("      already. Case folding is not a case operation with a tidy name;")
print("      it is the fold that makes two strings one KEY, and it inherits")
print("      a handful of compatibility mappings on the way.")
print()
print("   5 is merged by nothing, and it is the one that will actually reach")
print("      your database. A BOM is a legal character in the middle of a")
print("      string, it draws nothing, no normalization form removes it, and")
print("      casefold() keeps it too. The check it fails is not a comparison")
print("      at all -- it is a rule about which characters a field may hold.")
print()
print("   If you got 4 wrong you were reasoning from the NAME of the")
print("   function, which is the habit the whole page is arguing against.")

assert ud.normalize("NFC", PAIRS[0][0]) != PAIRS[0][1]
assert "\xb5".casefold() == "\u03bc"
