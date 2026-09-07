"""Answer key: five claims, and which of them survive without a version stamp.

This key deliberately prints NO version number and queries no recently-added
character. It cannot: it is checked against two operating systems and whatever
Python each runner ships, so anything version-dependent would make the answer
key a fact about the runner rather than about Unicode. That constraint is the
lesson -- the same reason a bug report needs the stamp.
"""
import unicodedata as ud

STABLE = [
    ("ud.name('A')", ud.name("A"), "assigned in 1991 and never touched"),
    ("ud.category('A')", ud.category("A"), "a letter, uppercase -- settled"),
    ("'ß'.upper()", "ß".upper(), "a case mapping fixed long ago"),
    ("len('😀'.encode())", len("😀".encode()), "UTF-8's rules, not the table's"),
]
print("CLAIMS THAT NEED NO VERSION")
for src, val, why in STABLE:
    print(f"   {src:<22} {str(val):<28} {why}")
print()
print("   Assignment is a one-way door: once a code point has a name and a")
print("   category, the consortium does not reassign it. So a claim about a")
print("   character that already existed when your Python was built is a claim")
print("   about Unicode, and it will read the same in five years.")
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
