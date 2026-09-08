"""The comparison is three questions, and the case where all three say nothing.

The example beside this one shows WHICH order a locale gives. This one shows
what a comparison is made of. UTS #10 -- the Unicode Collation Algorithm -- does
not compare two strings once. It compares them up to three times, on three keys,
in a fixed order: base letters, then accents, then case. A locale's data changes
the WEIGHTS; every locale on earth has this same shape.

The toy key below is that shape in about a dozen lines, which is enough to
reproduce all three rows of UTS #10's own Table 2 -- and enough to walk into the
problem the standard spends an appendix on: a collation exists in order to
IGNORE things, so it makes ties on purpose, and a tie is where a correct order
stops being a repeatable one.

Nothing here asks the machine for a locale, and no order below depends on one.
Every line is a fact about Unicode and about Python, and is the same on any
machine -- which on this page is the point rather than a convenience.

Run:  python3 sorting_and_collation_levels_py.py
"""

import unicodedata

ZWJ = "\u200d"   # ZERO WIDTH JOINER -- UTS #10's own example of an ignorable


def sort_key(s):
    """A toy three-level key, in UTS #10's shape.

    Not the algorithm: the algorithm is a weight table with a locale's
    tailoring on top of it, and section 5 of the other example builds the
    tailoring half. This is the SHAPE -- three keys, consulted in order, each
    answering a different question about the same string.
    """
    base, marks, case = [], [], []
    for ch in unicodedata.normalize("NFD", s):
        cat = unicodedata.category(ch)
        if cat == "Mn":                     # a combining mark: level 2 only
            if marks:
                marks[-1] += ch
            continue
        if cat == "Cf":                     # a format control: no level at all
            continue
        base.append(ch.casefold())          # level 1: the base letter
        marks.append("")
        case.append(0 if ch == ch.casefold() else 1)   # level 3: the case
    return ("".join(base), tuple(marks), tuple(case))


def det_key(s):
    """UTS #10 A.3.2: when the collation says equal, compare the raw strings."""
    return (sort_key(s), s)


def level_that_decides(a, b):
    """Which of the three keys is the first to differ -- or None."""
    for n, (x, y) in enumerate(zip(sort_key(a), sort_key(b)), start=1):
        if x != y:
            return n
    return None


def show(s):
    """A string with every invisible spelled out, so a fence can carry it.

    A combining mark draws on the character before it, so inside a code fence
    it is invisible to whoever wrote the fence as well as to the reader.
    """
    return "".join(ch if unicodedata.category(ch) not in ("Cf", "Mn")
                   and ch.isprintable()
                   else f"<U+{ord(ch):04X}>" for ch in s)


print("1. THREE KEYS, COMPARED IN ORDER -- UTS #10 TABLE 2, REPRODUCED")
print("-" * 72)
TABLE2 = [
    (1, "primary", "base letters", ["role", "roles", "rule"]),
    (2, "secondary", "accents", ["role", "rôle", "roles"]),
    (3, "tertiary", "case", ["role", "Role", "rôle"]),
]
for lvl, name, what, words in TABLE2:
    got = sorted(words, key=sort_key)
    print(f"   L{lvl}  {name:<10} {what:<13} {' < '.join(got)}"
          f"{'' if got == words else '   MISMATCH'}")
print()
print("   And the key itself, for the four words those three rows are built")
print("   from. Read down the columns rather than across:")
for w in ["role", "roles", "rôle", "Role"]:
    p, s, t = sort_key(w)
    marks = "(" + ", ".join(repr(show(m)) for m in s) + ")"
    print(f"     {w:<6} L1 {p!r:<9} L2 {marks:<40} L3 {t}")
print()
print("   L1 is the word with its accents and its case taken away. L2 is where")
print("   the accents went. L3 is where the case went. Nothing was discarded")
print("   and nothing was added up -- the string was taken apart into three")
print("   answers, and a comparison consults them in that order.")
print()

print("2. A LOWER LEVEL IS NOT A SMALLER VOTE. IT IS A LATER QUESTION")
print("-" * 72)
PAIRS = [
    ("role", "rule", "different base letters"),
    ("role", "rôle", "same letters, one accent"),
    ("role", "Role", "same letters, same accents, one capital"),
    ("rôle", "roles", "an accent AND a base-letter difference"),
]
for a, b, why in PAIRS:
    lvl = level_that_decides(a, b)
    print(f"   {a:<6} vs {b:<6}  decided at L{lvl}   ({why})")
print()
print("   The last row is the one to stare at. `rôle` carries an accent and")
print("   `roles` does not, and the accent never gets a vote: the base letters")
print("   already differ, so L1 answers and the comparison stops. Levels are")
print("   not weights in a sum -- each is a question asked only when every")
print("   question above it came back equal. That is why 'this locale cares")
print("   more about accents' is never the right description of a difference")
print("   between two locales; what differs is which level a character's")
print("   difference lands on.")
print()

print("3. AND THE CASE WHERE ALL THREE SAY NOTHING")
print("-" * 72)
A, B = "Davis", "Da" + ZWJ + "vis"
print(f"   a = {show(A)}")
print(f"   b = {show(B)}      the same name, plus one zero-width joiner")
print(f"   a == b                     {A == B}")
print(f"   sort_key(a) == sort_key(b) {sort_key(A) == sort_key(B)}")
print("   The joiner is a request about rendering, so a collation is right to")
print("   ignore it at every level -- and two strings that are not equal now")
print("   compare equal. That is not a defect. A collation exists in order to")
print("   ignore things: case at L1 and L2, accents at L1, a format character")
print("   everywhere. Ignoring anything means making ties on purpose.")
print()
print("   So ask the same question twice, changing only the input order:")
print(f"     sorted([a, b], key=sort_key)  ->  {[show(x) for x in sorted([A, B], key=sort_key)]}")
print(f"     sorted([b, a], key=sort_key)  ->  {[show(x) for x in sorted([B, A], key=sort_key)]}")
print()
print("   Same two strings, same key, two answers. Python's sorted() is STABLE,")
print("   which is exactly the mechanism: stability promises that equal")
print("   elements keep the order they arrived in, so the arrival order is")
print("   what you are reading back. Stability is a property of the sort")
print("   ALGORITHM and says nothing at all about the comparison -- which is")
print("   why it cannot rescue this. A list whose input order varies has no")
print("   fixed output order, however stable the sort that produced it.")
print()

print("4. THE FIX, AND THE STANDARD'S OWN OBJECTION TO IT")
print("-" * 72)
print("   UTS #10 A.3.2, in one line: when the collation says equal, fall")
print("   through to a comparison of the raw strings.")
print("     def det_key(s): return (sort_key(s), s)")
print(f"     sorted([a, b], key=det_key)  ->  {[show(x) for x in sorted([A, B], key=det_key)]}")
print(f"     sorted([b, a], key=det_key)  ->  {[show(x) for x in sorted([B, A], key=det_key)]}")
print("   One answer now, whatever order the rows arrive in. The tiebreak has")
print("   to be the raw code points and not a second collation, because code")
print("   point order is the one ordering no locale tailors, no library")
print("   version rewrites and no platform implements differently -- the only")
print("   part of this subject that is the same everywhere.")
print()
print("   And the objection, which is the standard's rather than this page's.")
print("   A.3.1 is titled 'Avoid Deterministic Comparisons' and gives three")
print("   reasons: the sort key roughly doubles in size, which a database pays")
print("   for; it does not make a non-deterministic SORT deterministic,")
print("   because that was never a property of the comparison; and the order")
print("   it produces is decided by differences nobody can see. Above, Davis")
print("   now precedes Da<U+200D>vis because of a character no font draws.")
print("   That order is not MEANINGFUL. It is only the same every time --")
print("   which is the whole trade, and is worth making only when something")
print("   downstream depends on two runs agreeing.")
print()

print("5. WHAT IT COSTS: A ROW ON TWO PAGES AND A ROW ON NONE")
print("-" * 72)
ROWS = ["Adams", "Baker", "Davis", "Da" + ZWJ + "vis", "Evans", "Foster"]
run1 = sorted(ROWS, key=sort_key)
run2 = sorted(ROWS[:2] + [ROWS[3], ROWS[2]] + ROWS[4:], key=sort_key)
print("   Six customers, one tie in the middle, three rows to a page.")
print(f"     page 1  (rows 0-2 of one query)   {[show(x) for x in run1[:3]]}")
print(f"     page 2  (rows 3-5 of the next)    {[show(x) for x in run2[3:]]}")
seen = [show(x) for x in run1[:3]] + [show(x) for x in run2[3:]]
print(f"     on both pages                     {sorted({x for x in seen if seen.count(x) > 1})}")
print(f"     on neither page                   {[show(x) for x in ROWS if show(x) not in seen]}")
print()
print("   Nothing failed. Both queries were correct and both used the same")
print("   collation; the second one merely saw the two tied rows in the other")
print("   order, which is all a database has to do differently -- a changed")
print("   plan, an updated row, two workers finishing out of order. The")
print("   reader gets one customer twice and never sees the other.")
print()
print("   The same shape reaches further than pagination: a nightly export")
print("   diffed against yesterday's shows moved lines nobody edited, a test")
print("   that sorts before asserting is green locally and red in CI, and")
print("   SELECT DISTINCT or sort -u drops a row that was not a duplicate.")
print()
print("   And where there is a unique field to reach for, reach for it")
print("   instead. UTS #10 A.1.1 says so: appending the primary key, a row")
print("   id or a sequence number is deterministic AND meaningful, and costs")
print("   nothing in key size. It is why `ORDER BY name, id` is the form to")
print("   write. Use the code point tiebreak when there is no such field.")

assert sorted(["role", "roles", "rule"], key=sort_key) == ["role", "roles", "rule"]
assert sorted(["role", "rôle", "roles"], key=sort_key) == ["role", "rôle", "roles"]
assert sorted(["role", "Role", "rôle"], key=sort_key) == ["role", "Role", "rôle"]
assert level_that_decides("rôle", "roles") == 1
assert sort_key(A) == sort_key(B) and A != B
assert sorted([A, B], key=sort_key) != sorted([B, A], key=sort_key)
assert sorted([A, B], key=det_key) == sorted([B, A], key=det_key)
