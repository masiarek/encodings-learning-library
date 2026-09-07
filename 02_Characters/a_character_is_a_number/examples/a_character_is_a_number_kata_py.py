"""Answer key: three ASCII tricks, and the edge each one falls off.

Every trick here is arithmetic on where the 1963 committee put things. That is
what makes them work, and it is also the whole of their range.
"""
print("1. ord('7') - ord('0')")
print(f"   {ord('7')} - {ord('0')} = {ord('7') - ord('0')}")
print("   The digits are ten consecutive codes starting at 0x30, so subtracting")
print("   the first one turns a digit into its value. It is not a conversion")
print("   routine; it is a subtraction that happens to be right.")
print()
print("2. x ^ 0x20 ON A LETTER")
for ch in "Aa":
    print(f"   {ch!r} {ord(ch):#04x} {ord(ch):08b}  ^0x20 -> {chr(ord(ch) ^ 0x20)!r}")
print("   Upper and lower differ in exactly ONE bit, because 0x41 and 0x61 are")
print("   0x20 apart and the alphabet is contiguous in both runs. So case is a")
print("   bit flip, both directions, with one operator and no table.")
print()
print("3. WHERE EACH ONE STOPS")
cases = [("'9'", "7"), ("full-width '７'", "７"), ("Arabic-Indic '٧'", "٧")]
for label, ch in cases:
    val = ord(ch) - ord("0")
    print(f"   {label:<22} ord-0x30 gives {val:<6} int() gives {int(ch)}")
print("   Two of those three are digits by Unicode's own definition -- int()")
print("   accepts them and str.isdigit() is True -- and the subtraction gives a")
print("   number in the thousands, because they are nowhere near 0x30.")
print()
print("   And the case trick:")
for ch in "éż":
    print(f"   {ch!r} {ord(ch):#06x}  ^0x20 -> {chr(ord(ch) ^ 0x20)!r}   upper() -> {ch.upper()!r}")
print("   The XOR gives a different letter, not a case change. Beyond 0x7F")
print("   nothing guarantees the two cases are 0x20 apart, or adjacent, or even")
print("   the same length -- 'sz' uppercases to two characters.")
print(f"   len('ß'.upper()) == {len('ß'.upper())}")

assert ord("7") - ord("0") == 7
assert chr(ord("A") ^ 0x20) == "a"
assert len("ß".upper()) == 2
