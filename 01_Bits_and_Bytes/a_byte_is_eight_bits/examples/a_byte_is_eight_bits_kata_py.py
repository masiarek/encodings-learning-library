"""Answer key: one byte, four readings, and the byte picks none of them.

The kata gives you 1010 1100 and asks for four numbers. Three of the four are
mechanical -- they are the same eight switches, written down in a different
base. The fourth is not: it depends on a decision made outside the byte.
"""

BITS = "10101100"
b = int(BITS, 2)

print(f"the byte              {BITS}")
print(f"unsigned              {b}")
print(f"hex                   {b:#04x}   ({b >> 4:04b} {b & 0xF:04b} -- one digit per nibble)")

# Two's complement by hand, which is what the kata asks you to do without a
# library: the top bit is set, so the value is what it would be minus 256.
signed = b - 256 if b & 0x80 else b
print(f"signed (two's compl.) {signed}   (top bit set, so {b} - 256)")
print(f"as Latin-1 text       {bytes([b]).decode('latin-1')!r}")
print()
print("Three of those four are the same fact written four ways: 172 and 0xac")
print("and 1010 1100 are one number in three notations, and nothing had to be")
print("decided to get from any of them to any other.")
print()
print("The fourth one is a DECISION. -84 is not hiding inside the switches; it")
print("is what you get if somebody agreed in advance that the top bit means a")
print("sign. Ask C: `char` is signed on most machines and unsigned on some, and")
print("the same byte then holds 172 or -84 with no cast anywhere in sight.")
print()
print("So the answer to 'which of the four does the byte decide?' is NONE of")
print("them. It holds eight switches. Everything else is a reader's agreement.")

check = format(b, "08b")
assert check == BITS, f"round trip failed: {check}"
assert signed == -84, signed
