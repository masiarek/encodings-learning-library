"""Answer key: the column no dump tool has, computed with unicodedata.

uni is on neither CI runner, so this key prints the same row uni would, from
the standard library -- which is also the answer to 'what do I do when it is
not installed'.
"""
import unicodedata as ud

def row(ch: str) -> None:
    cp = ord(ch)
    print(f"   {ch}  U+{cp:04X}  {cp:>7}  {ch.encode().hex(' '):<12} "
          f"&#{cp};  {ud.category(ch)}  {ud.name(ch, '(unnamed)')}")

print("   ch  code pt   decimal  utf-8         html      cat name")
for ch in "AéżЖ😀":
    row(ch)
print()
print("THE COLUMN THAT MATTERS IS THE LAST ONE")
print("   Every dump on your machine answers 'how is this stored?'. xxd, od and")
print("   hexdump all print the same bytes in different arrangements. None of")
print("   them will tell you WHAT the character is, because none of them has")
print("   the table -- and the name is the only identifier that is a standard")
print("   rather than one project's shorthand.")
print()
print("SEARCH BY NAME, WHICH IS THE OTHER HALF")
for name in ["LATIN SMALL LETTER Z WITH DOT ABOVE", "GRINNING FACE"]:
    ch = ud.lookup(name)
    print(f"   {name:<38} -> {ch}  U+{ord(ch):04X}")
print("   ud.lookup is the reverse of ud.name, and it is exact: the name is a")
print("   normative property, stable for the life of the code point, which is")
print("   why it is safe to write in source and in a bug report.")
print()
print("THE FOUR NAMES A CHARACTER HAS, AND WHICH ONE TO USE")
print("   the Unicode Name     LATIN SMALL LETTER E WITH ACUTE   -- normative")
print("   the code point       U+00E9                            -- normative")
print("   a compose sequence   <Compose> e '                     -- X11's table")
print("   a Vim digraph        e'                                -- Vim's table")
print("   The first two identify the character to any program. The last two")
print("   are input methods, they disagree with each other, and neither is a")
print("   name the character actually has.")
print()
print("WHEN uni IS NOT INSTALLED")
print("   python3 -c \"import unicodedata as u,sys;c=sys.argv[1];"
      "print(f'U+{ord(c):04X}',u.name(c))\" é")
print("   That is the row this key printed, and it needs nothing but Python.")

assert ud.name("é") == "LATIN SMALL LETTER E WITH ACUTE"
assert ud.lookup("GRINNING FACE") == "😀"
