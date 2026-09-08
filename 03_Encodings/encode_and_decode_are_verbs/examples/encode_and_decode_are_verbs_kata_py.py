"""Answer key: five lines, and which verb was applied with the wrong table.

Every bug in this field is one of these five shapes. The kata is to name the
shape before running the line.
"""
S = "café"
B = S.encode()                       # utf-8: 63 61 66 c3 a9

def show(label, fn):
    try:
        r = fn()
        kind = "str " if isinstance(r, str) else "bytes"
        print(f"   {label:<44} {kind} {r!r}")
    except (UnicodeDecodeError, UnicodeEncodeError) as e:
        print(f"   {label:<44} {type(e).__name__}")

print(f"start with   {S!r}   ->  utf-8 bytes {B.hex(' ')}")
print()
show("B.decode('utf-8')            round trip", lambda: B.decode("utf-8"))
show("B.decode('latin-1')          wrong table", lambda: B.decode("latin-1"))
show("B.decode('ascii')            table too small", lambda: B.decode("ascii"))
show("S.encode('latin-1')          works, and is lossy later", lambda: S.encode("latin-1"))
show("B.decode('latin-1').encode() decoded, re-encoded", lambda: B.decode("latin-1").encode())
print()
print("Line 1 is the only one that is a round trip: same table both ways.")
print()
print("Line 2 is MOJIBAKE, and notice that nothing failed. Latin-1 has a")
print("character for all 256 bytes, so it can never raise -- it just tells you")
print("the wrong thing, quietly, with an exit status of zero.")
print()
print("Line 3 is the good failure. ASCII has no character for c3, so the decode")
print("stops and says which byte and where. A table that CAN fail is a feature.")
print()
print("Line 4 succeeds and is the trap underneath a lot of legacy data: 'café'")
print("really does fit in Latin-1, so nothing warns you -- until the next")
print("string has a character Latin-1 has never heard of.")
print()
print("Line 5 is DOUBLE ENCODING, and this is the one that ruins databases.")
double = B.decode("latin-1").encode()
print(f"   {len(B)} bytes in, {len(double)} bytes out: {double.hex(' ')}")
print("   The text was decoded with the wrong table and then honestly encoded")
print("   with the right one, so the mojibake is now CORRECT UTF-8 of the wrong")
print("   characters. It round-trips perfectly from here on, which is exactly")
print("   why it survives every later check and reaches the user.")
print()
print("The verbs, one more time. ENCODE goes text -> bytes. DECODE goes bytes")
print("-> text. Each needs a named table, and neither can guess it: the bytes")
print("do not carry it.")

assert B.decode("latin-1") == "cafÃ©"
assert len(double) == 7
