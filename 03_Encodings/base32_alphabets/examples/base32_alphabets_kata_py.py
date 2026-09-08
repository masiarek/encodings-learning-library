"""Answer key: four Base32 menu entries, three of which differ only in symbols.

The kata's question is which of the four is a different ENCODING rather than a
different alphabet. The test is an input that is not a whole number of five-bit
pieces.
"""
import base64

RFC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
ZBASE = "ybndrfg8ejkmcpqxot1uwisza345h769"
CROCK = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

def retable(s: str, dst: str) -> str:
    return "".join(dst[RFC.index(c)] if c in RFC else c for c in s)

DATA = b"\x01\x02\x03\x04"          # 4 bytes = 32 bits: NOT a multiple of 5

std = base64.b32encode(DATA).decode()
hexb32 = base64.b32hexencode(DATA).decode()
print(f"input  {DATA.hex(' ')}   {len(DATA)*8} bits, and 32 is not a multiple of 5")
print()
print(f"   RFC 4648 standard   {std}")
print(f"   RFC 4648 base32hex  {hexb32}")
print(f"   z-base-32 symbols   {retable(std.rstrip('='), ZBASE)}")
print()
print("The first three are ONE encoding with three symbol tables. Same bit")
print("cutting, same padding, same length -- you can convert between them with")
print("a 32-entry lookup and nothing else. The alphabet is a presentation")
print("choice: base32hex sorts in the same order as the data, z-base-32 drops")
print("the characters people mistype.")
print()
print("CROCKFORD IS THE ODD ONE, AND HERE IS THE PROOF")
n = int.from_bytes(DATA, "big")
crock = ""
v = n
while v:
    crock = CROCK[v % 32] + crock
    v //= 32
print(f"   as a NUMBER            {n}  = 0x{n:x}")
print(f"   Crockford (base 32 of that number)   {crock}")
print(f"   RFC 4648 of the same bytes           {std}")
print()
print("They are not re-tablings of each other, and the reason is which end gets")
print("padded. RFC 4648 cuts the BIT STREAM from the left and zero-fills the")
print("last group on the RIGHT, then marks it with '='. Crockford is a notation")
print("for an INTEGER, so leading zeros are meaningless and any padding is on")
print("the LEFT -- there is no '=' because there is no partial group, only a")
print("smaller number.")
print()
print("So the two agree exactly when the input is a whole number of five-bit")
print("pieces and disagree otherwise:")
for data in (b"\x00\x00\x00\x00\x00", DATA):
    bits = len(data) * 8
    print(f"   {data.hex():<12} {bits:2d} bits, {bits % 5} left over -> "
          f"{'same shape' if bits % 5 == 0 else 'DIFFERENT ANSWERS'}")
print()
print("Which is why 'Base32' on a converter menu is not a specification. Ask")
print("which alphabet, and ask whether the thing being encoded is a byte string")
print("or a number -- those are two different questions and only one of them is")
print("about symbols.")

assert base64.b32decode(std) == DATA
assert std != hexb32
