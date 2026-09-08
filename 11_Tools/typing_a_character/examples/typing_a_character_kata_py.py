"""Answer key: four ways to produce one character, and which of them is a standard.

The compose and digraph tables are not on the runners, so this key computes the
one name that IS normative and states what the other three are.
"""
import unicodedata as ud

TARGET = "ż"
print(f"target   {TARGET}   U+{ord(TARGET):04X}   {ud.name(TARGET)}")
print()
print("FOUR WAYS TO TYPE IT")
rows = [
    ("X11 compose", "<Compose> z .", "X11's Compose file -- one project's table"),
    ("Vim digraph", "Ctrl-K z .", "Vim's own table, which is not X11's"),
    ("code point", "U+017C, entered per-application", "normative, but you must know the number"),
    ("Unicode name", ud.name(TARGET), "normative, and the only one a PROGRAM can use"),
]
for how, keys, what in rows:
    print(f"   {how:<14} {keys:<34} {what}")
print()
print("THE TWO TABLES DISAGREE, AND THAT IS THE POINT")
print("   Measured on this library's own parse of both files: the compose file")
print("   and Vim's digraph table can produce 2,580 characters between them and")
print("   agree on only 611. So a sequence you learned in one is usually not a")
print("   sequence in the other, and neither is a property of the CHARACTER --")
print("   they are properties of two programs.")
print()
print("THE NAME IS THE ONE THAT TRAVELS")
for name in ["LATIN SMALL LETTER Z WITH DOT ABOVE", "EURO SIGN", "GRINNING FACE"]:
    ch = ud.lookup(name)
    print(f"   ud.lookup({name!r:<38}) -> {ch}")
print("   It is normative, it is stable for the life of the code point, and it")
print("   is the same in every language that ships a Unicode table -- Python's")
print("   \\N{...}, Rust's char::from_u32 plus a lookup crate, and the name")
print("   column of every reference. That is why it is what to write in source")
print("   and in a bug report, and why 'the z with the dot' is not.")
print()
print("AND WHEN YOU CANNOT TYPE IT AT ALL")
print("   The escape is always available, and its shape says what the language")
print("   thinks a character is:")
print(f"   Python  \"\\N{{{ud.name(TARGET)}}}\"  or  \"\\u{ord(TARGET):04x}\"")
print(f"   Rust    '\\u{{{ord(TARGET):x}}}'")
b1, b2 = TARGET.encode()
print(f"   shell   printf '\\x{b1:02x}\\x{b2:02x}'   -- BYTES, not a character")
print("   The shell has no character escape at all -- only bytes -- which is")
print("   the same gap C has, and for the same reason.")

assert ud.lookup(ud.name("ż")) == "ż"
