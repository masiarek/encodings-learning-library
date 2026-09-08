"""Answer key: totals right to the cent, keys that match nothing."""
import csv, io

DOS = "id,amount\r\n1,10.50\r\n2,3.25\r\n"
UNIX = DOS.replace("\r\n", "\n")

print("THE SAME REPORT, TWO LINE ENDINGS")
print(f"   dos   {DOS.encode()[:12].hex(' ')} ...   {len(DOS.encode())} bytes")
print(f"   unix  {UNIX.encode()[:12].hex(' ')} ...   {len(UNIX.encode())} bytes")
print()
print("READ BOTH WITHOUT TELLING PYTHON ANYTHING")
for label, text in [("dos", DOS), ("unix", UNIX)]:
    rows = list(csv.DictReader(io.StringIO(text, newline="")))
    last = rows[-1]
    field = list(last)[-1]
    val = last[field]
    print(f"   {label:<5} last value {val!r:<10} float() -> {float(val)}   "
          f"key {field!r}")
print()
print("   The numbers are identical and correct to the cent. Now look at the")
print("   values as bytes -- that is where the difference is hiding.")
print()
print("WHERE THE EXTRA BYTE GOES")
rows = list(csv.reader(io.StringIO(DOS, newline="")))
print(f"   csv.reader with newline='' -> {rows}")
rows_bad = [ln.split(",") for ln in DOS.split("\n")]
print(f"   split('\\n')                 -> {rows_bad}")
print("   Splitting by hand leaves a 0d on the end of every last field. It")
print("   never shows on screen, it survives str.strip() only if you remember")
print("   to call it, and it makes '10.50\\r' a string that float() still")
print("   accepts -- so the totals come out right and the KEYS do not match.")
print()
print("THE COMPARISON THAT FAILS")
key_dos = DOS.split("\n")[1].split(",")[0]
print(f"   dos id field {key_dos!r} == '1' ? {key_dos == '1'}")
print("   That is the shape of the whole bug: arithmetic is fine because the")
print("   trailing byte is stripped by the number parser, and lookups fail")
print("   because they are not.")
print()
print("THE THREE FIXES, IN ORDER OF PREFERENCE")
print("   1. open(p, newline='') and let the csv module handle it -- it knows")
print("      about \\r\\n and it is the documented way to open a CSV.")
print("   2. open(p) in text mode with universal newlines, which translates")
print("      \\r\\n to \\n before your code sees it -- fine for line-oriented")
print("      data, wrong for csv, which needs to see the raw line endings.")
print("   3. .rstrip('\\r\\n') by hand, which works and which you will forget")
print("      exactly once.")
print()
print("AND THE ONE THAT IS NOT A FIX")
print(f"   'a\\r\\nb'.splitlines() -> {'a' + chr(13) + chr(10) + 'b'!r}.splitlines() = "
      f"{('a\r\nb').splitlines()}")
print("   splitlines() cuts on eleven different sequences, not one, so it will")
print("   also split a string containing U+2028 or a form feed. Right for text,")
print("   wrong for a format whose record separator is defined.")

assert float("10.50\r") == 10.5
assert "10.50\r" != "10.50"
