"""Answer key: which level decides each pair, and the pair no level decides.

The same toy three-level key as the lesson's own example, so the answers are
computed rather than asserted. Nothing here reads a locale, and every line is
the same on any machine.

Run:  python3 sorting_and_collation_kata_py.py
"""

import unicodedata

ZWJ = "\u200d"


def sort_key(s):
    """UTS #10's shape: base letters, then accents, then case."""
    base, marks, case = [], [], []
    for ch in unicodedata.normalize("NFD", s):
        cat = unicodedata.category(ch)
        if cat == "Mn":
            if marks:
                marks[-1] += ch
            continue
        if cat == "Cf":
            continue
        base.append(ch.casefold())
        marks.append("")
        case.append(0 if ch == ch.casefold() else 1)
    return ("".join(base), tuple(marks), tuple(case))


def det_key(s):
    return (sort_key(s), s)


def show(s):
    return "".join(ch if unicodedata.category(ch) not in ("Cf", "Mn")
                   and ch.isprintable()
                   else f"<U+{ord(ch):04X}>" for ch in s)


def decides(a, b):
    for n, (x, y) in enumerate(zip(sort_key(a), sort_key(b)), start=1):
        if x != y:
            return n
    return None


PAIRS = [
    ("role", "rule"),
    ("rôle", "roles"),
    ("role", "rôle"),
    ("role", "Role"),
    ("Davis", "Da" + ZWJ + "vis"),
]

print("WHICH LEVEL DECIDES")
for a, b in PAIRS:
    lvl = decides(a, b)
    order = " < ".join(show(x) for x in sorted([a, b], key=sort_key))
    print(f"   {show(a):<14} vs {show(b):<14}"
          f" {'L' + str(lvl) if lvl else 'none':<5}  {order}")
print()
print("   Row 2 is the one that catches people. An accent LOOKS like a level-2")
print("   difference, and it is -- but rôle and roles do not have the same base")
print("   letters, so L1 answers first and L2 is never consulted. A level is a")
print("   question asked only when every question above it came back equal.")
print()

A, B = PAIRS[-1]
print("THE PAIR NO LEVEL DECIDES")
print(f"   {show(A)!r} == {show(B)!r}            -> {A == B}")
print(f"   sort_key equal                       -> {sort_key(A) == sort_key(B)}")
print("   U+200D ZERO WIDTH JOINER is a rendering request. A collation is")
print("   right to ignore it -- and two unequal strings now compare equal, so")
print("   their order is not decided by the comparison at all.")
print()
print("   Same key, same two strings, two input orders:")
print(f"     sorted([a, b]) -> {[show(x) for x in sorted([A, B], key=sort_key)]}")
print(f"     sorted([b, a]) -> {[show(x) for x in sorted([B, A], key=sort_key)]}")
print("   Python's sorted() is stable, which is exactly why: stability keeps")
print("   equal elements in the order they arrived, so the arrival order is")
print("   what you are reading. Stability is a property of the sort algorithm;")
print("   it cannot make an order reproducible across two different inputs.")
print()

print("THE ONE-LINE FIX, AND WHAT IT BUYS")
print("   key=lambda s: (sort_key(s), s)      -- UTS #10, Appendix A.3.2")
print(f"     sorted([a, b]) -> {[show(x) for x in sorted([A, B], key=det_key)]}")
print(f"     sorted([b, a]) -> {[show(x) for x in sorted([B, A], key=det_key)]}")
print("   One answer, whatever order the rows arrive in. The tiebreak is the")
print("   raw code points, which is the only ordering no locale tailors and no")
print("   library version changes -- so it is the half of the key that is the")
print("   same on every machine and in every year.")
print("   It buys reproducibility and nothing else: Davis now precedes")
print("   Da<U+200D>vis because of a character no font draws. UTS #10 spends")
print("   section A.3.1 arguing you usually do not want this, and it is right")
print("   -- unless something downstream is paginating, diffing or caching the")
print("   order, in which case reproducibility IS the requirement.")

assert decides("role", "rule") == 1
assert decides("rôle", "roles") == 1
assert decides("role", "rôle") == 2
assert decides("role", "Role") == 3
assert decides(A, B) is None
assert sorted([A, B], key=sort_key) != sorted([B, A], key=sort_key)
assert sorted([A, B], key=det_key) == sorted([B, A], key=det_key)
