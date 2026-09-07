"""Answer key: five strings through the four preparation steps.

The kata asks which pairs collide after preparation and which survive it. The
useful surprise is that both answers are bugs, depending on what you were
storing.
"""
import unicodedata as ud

SAMPLES = ["ﬁle", "file", "ADMIN", "admin", "ａdmin", "Ⓐdmin"]

print(f"{'input':<10} {'NFKC':<10} {'+casefold':<12} {'code points'}")
for s in SAMPLES:
    k = ud.normalize("NFKC", s)
    f = k.casefold()
    print(f"{s:<10} {k:<10} {f:<12} {' '.join('%04X' % ord(c) for c in s)}")

print()
groups = {}
for s in SAMPLES:
    groups.setdefault(ud.normalize("NFKC", s).casefold(), []).append(s)
for key, members in groups.items():
    if len(members) > 1:
        print(f"   COLLIDE -> {key!r}: {members}")

print()
print("Four of the six become 'admin'. That is NFKC doing exactly its job: the")
print("ligature, the full-width letter and the circled letter are COMPATIBILITY")
print("spellings, and the whole point of the K forms is to fold them together.")
print()
print("Whether that is right depends entirely on what the string is for.")
print("  * A username -- yes. Two people must not be able to register names")
print("    that no human can tell apart, so you fold, and you store the folded")
print("    form as the key.")
print("  * A password -- no. Folding shrinks the keyspace, and NFKC maps many")
print("    characters to fewer, so it hands an attacker collisions for free.")
print("  * A display name -- no, and this is the one that gets broken by")
print("    accident: normalize in place and you have edited what somebody")
print("    wrote. Fold to COMPARE, store what they typed.")
print()
print("And the step order is not decoration. casefold-then-NFKC and")
print("NFKC-then-casefold can differ, which is why the specs pin the order:")
for s in ["ﬁ", "İ"]:
    a = ud.normalize("NFKC", s).casefold()
    b = ud.normalize("NFKC", s.casefold())
    mark = "same" if a == b else "DIFFERENT"
    print(f"   {s!r:<6} NFKC->casefold {a!r:<10} casefold->NFKC {b!r:<10} {mark}")

assert ud.normalize("NFKC", "ﬁle") == "file"
