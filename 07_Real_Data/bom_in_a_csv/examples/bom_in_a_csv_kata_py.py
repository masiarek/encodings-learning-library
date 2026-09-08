"""Answer key: three bytes that are both the fix and the bug."""
import csv, io

ROWS = "ID,name\n1,Ada\n2,Bo\n"
plain = ROWS.encode("utf-8")
with_bom = ROWS.encode("utf-8-sig")

print(f"without BOM  {plain[:8].hex(' ')} ...")
print(f"with BOM     {with_bom[:8].hex(' ')} ...")
print()
print("READ THE BOM'D FILE FOUR WAYS")
for enc in ["utf-8", "utf-8-sig"]:
    for data, label in [(with_bom, "BOM'd"), (plain, "plain")]:
        text = data.decode(enc)
        first = next(csv.DictReader(io.StringIO(text)))
        key = list(first)[0]
        ok = key == "ID"
        print(f"   {label:<6} read as {enc:<10} first key {key!r:<12} "
              f"row['ID'] would {'work' if ok else 'raise KeyError'}")
print()
print("   utf-8-sig is the only reading that works on BOTH files: it strips the")
print("   mark if it is there and does nothing if it is not. That is the whole")
print("   recommendation for reading a CSV that might have come from Excel.")
print()
print("WHAT THE BROKEN KEY ACTUALLY IS")
bad = list(csv.DictReader(io.StringIO(with_bom.decode("utf-8"))))[0]
key = list(bad)[0]
print(f"   repr          {key!r}")
print(f"   code points   {' '.join('U+%04X' % ord(c) for c in key)}")
print(f"   it prints as  {key}   -- indistinguishable from ID on any screen")
print("   U+FEFF is ZERO WIDTH NO-BREAK SPACE. It draws nothing, it is not")
print("   whitespace to strip(), and it makes the header look perfectly correct")
print("   in the KeyError message that mentions it.")
print()
print("AND NOW THE OTHER DIRECTION, WHICH IS WHY THIS IS NOT SIMPLY A BUG")
print("   Excel on Windows reads a UTF-8 CSV correctly only if the BOM is")
print("   there; without it, it falls back to the system code page and the")
print("   accented names arrive as mojibake. So the same three bytes are:")
print("       the FIX      for a person double-clicking the file")
print("       the BUG      for the program parsing it")
print("   There is no setting that is right for both, which means the skill is")
print("   not 'strip BOMs' -- it is knowing which of the two consumers a given")
print("   file is for, and writing it accordingly.")
print()
print("WRITING, THE TWO WAYS")
print(f"   open(p,'w',encoding='utf-8')      -> {plain[:3].hex(' ')} ...  for programs")
print(f"   open(p,'w',encoding='utf-8-sig')  -> {with_bom[:3].hex(' ')}  for Excel")

assert list(csv.DictReader(io.StringIO(with_bom.decode("utf-8-sig"))))[0]["ID"] == "1"
assert "﻿" in with_bom.decode("utf-8")
