"""Answer key: what rg decides differently, computed without rg.

rg is on neither CI runner, so the rules are demonstrated with the standard
library doing the same job. The claims are about rg's documented behaviour and
each one is checkable against a program here.
"""
TEXT = "café\n"

print("1. rg NEVER ASKS THE LOCALE")
print("   grep takes its definition of a character from LC_CTYPE, so the same")
print("   pattern gives different answers in different environments. rg has no")
print("   locale code path at all: patterns and haystacks are UTF-8 by")
print("   default, everywhere, on every platform. One implementation, one")
print("   answer -- which is the single biggest reason to reach for it.")
print()
print("2. IT READS THE BOM, WHICH IS WHY IT CAN SEARCH UTF-16")
for enc, label in [("utf-8", "utf-8, no mark"), ("utf-8-sig", "utf-8 + signature"),
                   ("utf-16", "utf-16 + BOM"), ("utf-16-le", "utf-16-le, NO mark"),
                   ("utf-32", "utf-32 + BOM")]:
    b = TEXT.encode(enc)
    marks = {b"\xef\xbb\xbf": "UTF-8", b"\xff\xfe": "UTF-16LE", b"\xfe\xff": "UTF-16BE"}
    found = next((n for m, n in marks.items() if b.startswith(m)), None)
    # UTF-32LE starts with the same two bytes as UTF-16LE, then two NULs.
    if b.startswith(b"\xff\xfe\x00\x00"):
        found = "UTF-32LE mark -- and rg tests only three, so it reads this as UTF-16LE"
    print(f"   {label:<22} {b[:4].hex(' '):<12} -> {found or 'nothing; searched as raw bytes'}")
print()
print("   Three marks are tested, and UTF-32 is not one of them. A UTF-16 file")
print("   WITHOUT a BOM is also searched as raw bytes -- so 'rg reads UTF-16'")
print("   is true only of files that announce themselves.")
print()
print("3. --column COUNTS BYTES, AND SAYS SO")
line = "café x"
print(f"   {line!r}")
print(f"   the x is character {line.index('x') + 1}, and byte {len(line[:line.index('x')].encode()) + 1}")
print("   rg reports the byte offset. That is the honest number for a tool")
print("   that works in bytes, and it is not the number an editor's cursor")
print("   shows -- so a script that jumps to rg's column lands one place early")
print("   on any line containing a multi-byte character.")
print()
print("4. WHAT IT SKIPS BY DEFAULT, WHICH IS NOT AN ENCODING QUESTION")
print("   rg respects .gitignore, skips hidden files and skips binary files")
print("   unless told otherwise. Those are three separate defaults, three")
print("   separate flags (-u, -uu, -uuu stack them off), and every one of them")
print("   can make a search come back empty on a file that is right there.")
print("   grep has none of these defaults, which is why the two tools")
print("   disagreeing usually has nothing to do with the pattern.")

assert "café\n".encode("utf-8-sig").startswith(b"\xef\xbb\xbf")
assert "café\n".encode("utf-32").startswith(b"\xff\xfe\x00\x00")
