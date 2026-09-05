"""The same split in Python: str and bytes — but the promise is checked later, and less."""

noodles = "noodles"
oodles = noodles[1:]
poodles = "ಠ_ಠ"

print("1. PYTHON COUNTS CHARACTERS WHERE RUST COUNTS BYTES")
print("   name      value       len(str)          len(str.encode())")
for name, s in (("noodles", noodles), ("oodles", oodles), ("poodles", poodles)):
    print(f"   {name:<8}  {s:<10}  {len(s):>2} characters       {len(s.encode()):>2} bytes")
print("   Rust's String.len() is the RIGHT-hand column. Python's len() is the left one.")
print("   For 'noodles' they agree, which is why the difference stays hidden until it doesn't.")
print()

print("2. THE TWO TYPES, AND THE TWO VERBS BETWEEN THEM")
print(f"   type(poodles)            = {type(poodles).__name__}")
print(f"   type(poodles.encode())   = {type(poodles.encode()).__name__}")
print(f"   poodles.encode().hex(' ') = {poodles.encode().hex(' ').upper()}")
print("   .encode() str -> bytes    .decode() bytes -> str    and neither happens by itself")
print()

print("3. WHERE THE CHECK HAPPENS: NOT AT CONSTRUCTION")
truncated = poodles.encode()[:-1]          # drop the last byte of the last 'ಠ'
print(f"   truncated = {truncated!r}")
print(f"   len(truncated) = {len(truncated)} — Python built this object without complaint.")
print("   A bytes object has made no promise, so it can hold this forever.")
try:
    truncated.decode()
except UnicodeDecodeError as e:
    print(f"   truncated.decode() -> UnicodeDecodeError: {e.reason}")
    print(f"   start={e.start} end={e.end} — the same index Rust's valid_up_to() reports")
print("   Rust puts this check at String::from_utf8. Python puts it at .decode(). Same check, later.")
print()

print("4. errors= IS THE CHOICE from_utf8_lossy MAKES FOR YOU")
for mode in ("replace", "ignore", "backslashreplace"):
    print(f"   truncated.decode(errors={mode!r}) -> {truncated.decode(errors=mode)!r}")
print("   Rust offers exactly one of these in std: from_utf8_lossy, which is errors='replace'.")
print()

print("5. THE ONE PYTHON MAKES EASY THAT RUST REFUSES")
print(f"   poodles[0] = {poodles[0]!r}   — Python indexes by CHARACTER, so this just works")
print("   Rust will not compile s[0], because byte 0 is E0 and that is not a character.")
print("   Python's answer is friendlier and hides the question; Rust's is ruder and cannot.")
