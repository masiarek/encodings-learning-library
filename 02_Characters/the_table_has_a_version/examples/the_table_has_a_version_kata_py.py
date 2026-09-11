"""Answer key: five claims, and which of them survive without a version stamp.

This key deliberately prints NO version number and queries no recently-added
character. It cannot: CI pins Python only to a minor version, which will move,
and a reader runs whatever Python they have, so anything version-dependent
would make the answer key a fact about the interpreter rather than about
Unicode. That constraint is the lesson -- the same reason a bug report needs
the stamp.
"""
import unicodedata as ud


def show(rows):
    for src, val, why in rows:
        print(f"   {src:<22} {str(val):<28} {why}")


print("CLAIMS THAT NEED NO VERSION")
show([
    ("ud.name('A')", ud.name("A"), "guaranteed: the stability policy"),
    ("len('😀'.encode())", len("😀".encode()), "arithmetic: UTF-8's rules, not the table's"),
])
print()
print("   Assignment is a one-way door: once a code point is assigned, its")
print("   name never changes and the code point is never reused. That is")
print("   written into Unicode's stability policy, and it is why claim 1")
print("   needs no stamp. The byte count needs none for another reason:")
print("   UTF-8 encodes the number without asking the table what it means.")
print()
print("CLAIMS THAT ARE OBSERVED, NOT GUARANTEED")
show([
    ("ud.category('A')", ud.category("A"), "observed: never promised"),
    ("'ß'.upper()", "ß".upper(), "observed: a row in SpecialCasing.txt"),
])
print()
print("   Claim 2 is the trap. It looks as settled as claim 1, and it is not")
print("   the same kind of claim: the policy pins a name, but not the Lu on")
print("   'A' and not the SS in 'ß'. Both kinds of answer have moved for")
print("   characters that were already assigned. ZERO WIDTH SPACE was a")
print("   space (Zs) in the 2002 table and is a format character (Cf) in a")
print("   modern one. U+019B and U+0264, in Unicode since 1993, had no")
print("   capital until Unicode 16.0 gave each one -- so what upper() returns")
print("   for them changed thirty-one years after they were encoded.")
print()
print("   Nobody expects 'A' or 'ß' to move. That is a forecast, not a")
print("   promise, so claim 2 sorts with 3, 4 and 5: the version stamp is")
print("   what keeps a bug report true on the day a forecast fails.")
print()
print("CLAIMS THAT DO NOT SURVIVE WITHOUT ONE")
for src, why in [
    ("unicodedata.unidata_version", "the whole question -- and it is a property of the LIBRARY, not the machine"),
    ("how many code points are assigned", "grows every release; ~5,000 were added in one recent year"),
    ("ud.name(chr(0x1FA00 + n))", "raises for a character not yet in YOUR table, and returns a name in a newer one"),
    ("whether a string 'is emoji'", "the emoji list is versioned separately from Unicode itself"),
    ("str.isprintable() on a recent char", "depends on a category your table may not have yet"),
]:
    print(f"   {src:<38} {why}")
print()
print("THE PART THAT SURPRISES PEOPLE")
print("   There is no 'the' Unicode version on a computer. Every language ships")
print("   its OWN copy of the table: Python's is in unicodedata, Rust's is")
print("   compiled into core, your database has another, and your browser a")
print("   fourth. They are updated on different schedules by different people,")
print("   so two programs on one machine can disagree about whether a character")
print("   exists -- and neither is out of date, exactly. They were built at")
print("   different times.")
print()
print("   That is why the version belongs in the bug report next to the output,")
print("   and why 'it works on my machine' has one more meaning here than it")
print("   does anywhere else.")
print()
print("HOW TO ASK EACH ONE, WHEN YOU NEED THE STAMP")
print("   python3 -c 'import unicodedata; print(unicodedata.unidata_version)'")
print("   rustc         -- see char::UNICODE_VERSION in core")
print("   psql          -- SELECT icu_unicode_version();")
print("   node          -- process.versions.unicode")

assert ud.name("A") == "LATIN CAPITAL LETTER A"
assert "ß".upper() == "SS"
