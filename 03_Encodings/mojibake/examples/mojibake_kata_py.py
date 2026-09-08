"""Answer key: name the culprit from the garbage alone.

Each line is one string that went through one wrong step. The kata is to read
the pattern backwards to the pair of tables that produced it.
"""
WORD = "café"

CASES = [
    ("utf-8 read as latin-1",  WORD.encode("utf-8").decode("latin-1")),
    ("utf-8 read as cp1252",   WORD.encode("utf-8").decode("cp1252")),
    ("utf-8 read as cp437",    WORD.encode("utf-8").decode("cp437")),
    ("double encoded",         WORD.encode("utf-8").decode("latin-1").encode("utf-8").decode("latin-1")),
    ("latin-1 read as utf-8",  WORD.encode("latin-1").decode("utf-8", "replace")),
]
print(f"the word   {WORD!r}   utf-8 {WORD.encode().hex(' ')}   latin-1 {WORD.encode('latin-1').hex(' ')}")
print()
for label, garbled in CASES:
    # The code points, not just the glyph: two of these contain characters
    # that draw as nothing at all, and the count is half the evidence.
    pts = " ".join("%04X" % ord(c) for c in garbled)
    print(f"   {garbled:<12} {len(garbled)} chars   {label}")
    print(f"   {'':<12} {pts}")
print()
print("THE TELLS")
print("   Ã  before the accented letter  -> utf-8 read as a Latin-1-ish table.")
print("      c3 is A-tilde in every one of them, so the leading character is")
print("      almost always Ã and the SECOND character names the table.")
print("   Ã© vs Ã©  -> Latin-1 and cp1252 differ only above 0x7F, and a9 is")
print("      the same in both here; change the letter and they separate.")
print("   Box- and line-drawing characters -- caf|- and the like -> a DOS code")
print("      page such as cp437, whose top half is not letters at all.")
print("   SEVEN characters where the single-pass cases have five -- four in")
print("      place of the letter instead of two, one of them")
print("      U+0083, a C1 control that draws as nothing -> DOUBLE ENCODED. The")
print("      glyphs alone will not tell you; the length and the code points")
print("      will. Each pass through the wrong table roughly doubles the byte")
print("      count and drags in characters nobody can see.")
print("   U+FFFD  -> the opposite direction. Latin-1 bytes read as UTF-8 do not")
print("      form valid sequences, so a strict decoder RAISES and a lenient one")
print("      substitutes. This is the only case in the list that a program can")
print("      notice on its own.")
print()
print("WHICH ONES ARE REPAIRABLE")
broken = WORD.encode("utf-8").decode("latin-1")
print(f"   {broken!r}.encode('latin-1').decode('utf-8') -> {broken.encode('latin-1').decode('utf-8')!r}")
print("   Latin-1 is TOTAL -- every byte 00..FF has a character -- so the trip")
print("   through it loses nothing and reverses exactly.")
print()
print("   cp1252 is not total: five byte values are unassigned. If the text")
print("   passed through one of them the information is gone, and the repair")
print("   raises instead of quietly returning something wrong -- which is the")
print("   behaviour you want at that point.")
print()
print("   And the replacement characters are not repairable at all. U+FFFD is")
print("   not a record of what was there; it is a record that something was.")

assert WORD.encode("utf-8").decode("latin-1") == "cafÃ©"
assert "cafÃ©".encode("latin-1").decode("utf-8") == "café"
