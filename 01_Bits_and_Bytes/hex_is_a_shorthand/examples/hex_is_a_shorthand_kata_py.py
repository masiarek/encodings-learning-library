"""Answer key: four bits at a time, in both directions.

Each conversion is done nibble by nibble and printed that way, because doing it
in one step with hex() is the thing the kata is asking you NOT to do.
"""

def nibbles(byte: int) -> str:
    return f"{byte >> 4:04b} {byte & 0xF:04b}"

print("HEX TO BITS -- split the byte, convert each half")
for byte in (0xC3, 0xA9):
    hi, lo = byte >> 4, byte & 0xF
    print(f"   {byte:#04x} -> {hi:X} and {lo:X} -> {hi:04b} and {lo:04b} -> {byte:08b}")

print()
print("BITS TO HEX -- same move, the other way")
bits = "11101001"
hi, lo = int(bits[:4], 2), int(bits[4:], 2)
print(f"   {bits[:4]} {bits[4:]} -> {hi:X} and {lo:X} -> {int(bits, 2):#04x}")

print()
print("THE TWO BYTES TOGETHER")
print(f"   C3 A9 -> {nibbles(0xC3)} {nibbles(0xA9)}")
print("   Sixteen switches, four hex digits, and no arithmetic anywhere: each")
print("   digit is a picture of exactly four bits and never borrows from its")
print("   neighbour. That is the whole reason hex won.")

print()
print("NOW THE SAME BYTES IN OCTAL, WHICH DOES BORROW")
octal = format(0xC3A9, "o")
print(f"   0xC3A9 = 0o{octal}")
print("   Three bits per digit against sixteen bits, so the digits do not line")
print("   up with the bytes: the boundary between C3 and A9 falls INSIDE an")
print("   octal digit. Read the two bytes separately and you get")
print(f"   0o{format(0xC3, 'o')} and 0o{format(0xA9, 'o')}, whose digits are nowhere in 0o{octal}"
      " except by accident.")
print("   Sixteen is a power of two that divides eight. Eight is not.")

assert format(0xC3, "08b") == "11000011"
assert int("11101001", 2) == 0xE9
