"""Answer key: a 31-character hash field, and three tools that all accept it.

The kata is not a conversion exercise. It asks what each of three readings does
with an odd-length hex string, which one you want, and where the check goes.
"""

FIELD = "d131dd02c5e6eec4693d9a0698aff95c" [:-1]      # 31 characters: one lost
print(f"the field   {FIELD!r}   ({len(FIELD)} characters, described as '32 hex')")
print()

print("1. AS A NUMBER -- int(s, 16)")
n = int(FIELD, 16)
print(f"   accepted, value {n:#x}")
print("   A number has no width, so 31 digits is not short, it is just smaller.")
print("   Nothing is missing from a number's point of view. Notice what the")
print("   round trip does: it comes back with a LEADING ZERO restored in a")
print(f"   place the sender never had one -- {n:032x}")
print("   That is the corruption, and it looks like a repair.")
print()

print("2. AS BYTES -- bytes.fromhex(s)")
try:
    bytes.fromhex(FIELD)
except ValueError as e:
    print(f"   ValueError: {e}")
print("   The width IS the data here, and 31 does not divide by 2, so Python")
print("   refuses. This is the reading you want: it is the only one of the")
print("   three that knows a hash is 16 bytes rather than a large integer.")
print()

print("3. AS BYTES, THE SHELL'S WAY -- xxd -r -p")
print("   Silently drops the last nibble and exits 0. The page's own one-liner")
print("   shows it: printf '123' | xxd -r -p | xxd -p prints 12.")
print("   Fifteen and a half bytes are not representable, so it writes fifteen")
print("   and says nothing. A pipeline reading its status sees success.")
print()

print("WHERE THE CHECK GOES")
print("   At the boundary, before the value becomes an object -- the same place")
print("   every decode belongs. Two lines, and they are not the same check:")
print("       if len(field) != 32: reject      # the width, which is the contract")
print("       raw = bytes.fromhex(field)       # the alphabet, which is the parser's")
print("   The second one alone would pass a 30-character field. The first alone")
print("   would pass 32 characters of Arabic-Indic digits, which int() accepts")
print(f"   and which are not hex at all: int('\\u0664\\u0661', 16) == {int('٤١', 16)}.")

assert len(FIELD) == 31
assert f"{n:032x}".startswith("0"), "the round trip invents a leading zero"
