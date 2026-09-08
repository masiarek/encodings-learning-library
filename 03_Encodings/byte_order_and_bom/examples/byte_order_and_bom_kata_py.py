"""Answer key: one two-letter string, five encodings, and the column name bug.

The kata asks for the exact bytes before running anything, then for what a CSV
reader does with the first column.
"""
S = "ID"
ENCS = ["utf-8", "utf-8-sig", "utf-16", "utf-16-le", "utf-16-be", "utf-32"]

print(f"{'encoding':<12} {'bytes':<28} {'len':>3}  mark?")
for e in ENCS:
    b = S.encode(e)
    mark = ("BOM " + b[:2].hex().upper()) if e.startswith("utf-16") and b[:2] in (b"\xff\xfe", b"\xfe\xff") else ""
    if e == "utf-8-sig":
        mark = "signature EF BB BF"
    if e == "utf-32":
        mark = "BOM, 4 bytes of it"
    print(f"{e:<12} {b.hex(' '):<28} {len(b):>3}  {mark}".rstrip())
print()
print("utf-16 with no suffix WRITES A BOM and picks an order for you; the -le")
print("and -be forms write neither, because you already said which. That is the")
print("whole job of the mark: a value wider than one byte has to go into the")
print("file in some order, and U+FEFF first lets the reader work out which.")
print()
print("UTF-8 HAS NO ORDER TO RESOLVE, AND GETS THE MARK ANYWAY")
print(f"   utf-8      {S.encode('utf-8').hex(' ')}")
print(f"   utf-8-sig  {S.encode('utf-8-sig').hex(' ')}   <- the same three bytes, every time")
print("   Bytes cannot be in the wrong order when the unit IS a byte. Those")
print("   three bytes are a SIGNATURE -- a label saying 'this is UTF-8' -- and")
print("   Windows tools write it so Notepad can tell UTF-8 from a code page.")
print()
print("AND HERE IS THE CSV BUG, IN FULL")
raw = "ID,name\n1,Ada\n".encode("utf-8-sig")
plain = raw.decode("utf-8")
fixed = raw.decode("utf-8-sig")
print(f"   file starts   {raw[:8].hex(' ')}")
print(f"   read as utf-8      first column {plain.split(',')[0]!r}")
print(f"   read as utf-8-sig  first column {fixed.split(',')[0]!r}")
print(f"   equal to 'ID'?     {plain.split(',')[0] == 'ID'} and {fixed.split(',')[0] == 'ID'}")
print()
print("   The first column is not called ID. It is called ZERO WIDTH NO-BREAK")
print("   SPACE followed by ID, and it draws as 'ID' on every screen you will")
print("   look at. row['ID'] raises KeyError, the header LOOKS right in the")
print("   error message, and this is the single most reported bug in this")
print("   chapter. The fix is to name the encoding utf-8-sig when reading a")
print("   file that might have come from Excel -- it strips the mark if it is")
print("   there and does nothing if it is not.")

assert "ID,name\n".encode("utf-8-sig").startswith(b"\xef\xbb\xbf")
assert "ID,name\n".encode("utf-8-sig").decode("utf-8")[0] == "﻿"
