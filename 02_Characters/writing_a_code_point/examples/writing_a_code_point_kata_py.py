"""Answer key: five ways to write one character, and what each form assumes.

The kata asks what each escape produces and -- the real question -- which of
them can write U+1F600 at all.
"""
FORMS = [
    (r'"\xe9"',                              "\xe9",  "a BYTE value, extended to a code point"),
    ('"' + chr(92) + 'u00e9"',           "\u00e9", "a 16-bit code unit"),
    (r'"\U000000e9"',                        "\U000000e9", "a full 32-bit scalar value"),
    (r'"\N{LATIN SMALL LETTER E WITH ACUTE}"', "\N{LATIN SMALL LETTER E WITH ACUTE}", "a NAME, looked up in the table"),
]
print("FOUR SPELLINGS OF ONE CHARACTER")
for src, val, what in FORMS:
    print(f"   {src:<40} -> {val!r}  U+{ord(val):04X}   {what}")
print(f"   all four equal? {len({v for _, v, _ in FORMS}) == 1}")
print()

print("NOW U+1F600, WHICH IS ABOVE U+FFFF")
print(r'   "\U0001F600"  ->', repr("\U0001F600"), " works: \\U takes a scalar value")
print('   "' + chr(92) + 'u1F600"      ->  NOT that character: ' + chr(92) + 'u reads exactly four')
print('                     digits, so it is U+1F60 then the digit 0 ->', repr("\u1F60" + "0"))
print()
print("That four-digit limit is the whole lesson. \\u is a UTF-16 CODE UNIT")
print("escape, and a code unit is 16 bits, so it cannot name anything above")
print("U+FFFF on its own. Java and JSON have only that form, which is why a")
print("JSON emoji is written as a SURROGATE PAIR:")
hi, lo = "😀".encode("utf-16-be")[:2], "😀".encode("utf-16-be")[2:]
print(f"   \\u{int.from_bytes(hi, 'big'):04X}\\u{int.from_bytes(lo, 'big'):04X}"
      "   -- two escapes, one character, and neither half is a character")
print()
print("So the escape a language gives you is a statement about what it thinks")
print("a character IS:")
print("   Rust   \\u{1F600}   a scalar value, any width, braces so it can be")
print("   Python \\U0001F600  a scalar value, fixed 8 digits -- plus \\N{...},")
print("                      the only form that names rather than numbers")
print("   Java   \\uD83D\\uDE00  two UTF-16 code units, because that is its str")
print("   C      none of the above -- \\x is bytes, and what those bytes MEAN")
print("          is the compiler's execution charset, not a string feature")

assert "\xe9" == "é" == "\N{LATIN SMALL LETTER E WITH ACUTE}"
assert "\u1F60" + "0" != "\U0001F600"
