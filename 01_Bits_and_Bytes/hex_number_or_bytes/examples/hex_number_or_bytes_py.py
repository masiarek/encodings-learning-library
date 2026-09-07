#!/usr/bin/env python3
"""The same hex digits, read two ways -- and the two doors in Python that
read them.

`int(s, 16)` gives you a NUMBER: width is nothing, leading zeros are noise,
and there is no such thing as its byte order. `bytes.fromhex(s)` gives you
BYTES: width is the data, a leading zero is a byte, and an odd number of
digits is not a value at all.

Run:  python3 hex_number_or_bytes_py.py
"""

import unicodedata

RULE = "-" * 72


def say(title: str) -> None:
    print(f"\n{title}\n{RULE}")


say("1. ONE STRING, TWO OBJECTS")

s = "0041"
n = int(s, 16)
b = bytes.fromhex(s)
print(f"   {'the string':<26} {s!r}")
print(f"   {'int(s, 16)':<26} {n:<10} a number: 65, and nothing else is claimed")
print(f"   {'bytes.fromhex(s)':<26} {b!r:<10} two bytes: 00 41")
print(f"   {'len of each':<26} {'-':<10} a number has no length; the bytes have {len(b)}")
print()
print("   Both readings are correct and they are not the same object. Which")
print("   one a hex string means is not in the string -- it is in the field")
print("   it came out of, and that is what an interface agreement is for.")

say("2. LEADING ZEROS ARE NOISE, OR THEY ARE A NUL BYTE")

pairs = [("41", "0041"), ("ff", "00ff"), ("0a", "00000a")]
print(f"   {'a':<8} {'b':<8} {'int(a)==int(b)':<16} {'fromhex':<28}")
for a, bb in pairs:
    same = int(a, 16) == int(bb, 16)
    try:
        fa = bytes.fromhex(a)
        fb = bytes.fromhex(bb)
        cmp = f"{fa!r} vs {fb!r}"
    except ValueError as exc:
        cmp = f"ValueError ({exc})"
    print(f"   {a!r:<8} {bb!r:<8} {str(same):<16} {cmp:<28}")
print()
print("   As numbers every row is a pair of equals. As bytes, no row is:")
print("   '0041' is a NUL followed by an 'A', and a NUL byte is the one that")
print("   truncates a C string, ends a field, or fails a database insert.")
print("   Padding a number is cosmetic; padding a byte string is editing it.")

say("3. A NUMBER HAS NO BYTE ORDER. BYTES DO.")

v = 0x41
for order in ("big", "little"):
    print(f"   {f'(0x41).to_bytes(2, {order!r})':<34} {v.to_bytes(2, order).hex(' ')}")
print(f"   {'and back, big':<34} {int.from_bytes(bytes.fromhex('0041'), 'big')}")
print(f"   {'and back, little':<34} {int.from_bytes(bytes.fromhex('0041'), 'little')}")
print()
print("   `to_bytes` will not let you leave the question out -- the argument")
print("   has no default, because there is no right answer. Note what that")
print("   means about the string in section 1: '0041' as a NUMBER is 65 on")
print("   every machine ever built, and as BYTES it is 65 or 16640 depending")
print("   on a convention the digits do not record.")

say("4. AN ODD NUMBER OF DIGITS: FINE, FATAL, OR SILENTLY HALVED")

odd = "123"
print(f"   {'int(odd, 16)':<26} {int(odd, 16):<12} a number needs no even width")
try:
    bytes.fromhex(odd)
except ValueError as exc:
    print(f"   {'bytes.fromhex(odd)':<26} {'ValueError':<12} {exc}")
print(f"   {'xxd -r -p (shell run)':<26} {'0x12':<12} drops the trailing nibble, exit 0, no message")
print()
print("   Three tools, three different answers to one malformed input, and")
print("   only the middle one tells you. An odd-length hex field is almost")
print("   always a truncated one -- a log line cut at a column limit, a copy")
print("   that missed a character -- so the answer you want is the ValueError.")

say("5. WHAT int(s, 16) WILL SWALLOW")

cases = ["41", "0x41", "0X41", "4_1", " 41 ", "41\n", "+41", "-41", "٤١", "4G", ""]
print(f"   {'input':<12} {'int(s, 16)':<14} {'bytes.fromhex(s)':<20}")
for c in cases:
    try:
        a = str(int(c, 16))
    except ValueError:
        a = "ValueError"
    try:
        r = repr(bytes.fromhex(c))
    except ValueError:
        r = "ValueError"
    print(f"   {c!r:<12} {a:<14} {r:<20}")
print()
print("   The prefix, an underscore, surrounding whitespace, a newline and a")
print("   sign all pass. So does the ninth row, which is worth naming:")
for ch in "٤١":
    print(f"     {ch!r}  U+{ord(ch):04X}  {unicodedata.name(ch)}")
print("   Two ARABIC-INDIC digits -- not in this library's cast, and here")
print("   because nothing else has the property: they are not ASCII, they")
print("   are not in '0123456789abcdefABCDEF', and int() takes them anyway.")
print("   int() accepts any Unicode character with a decimal digit value, in")
print("   every base, so a hex field validated by `int(s, 16)` accepts digits")
print("   your regex, your database and your partner's parser will not.")
print()
print("   And the last two rows are the pair to keep straight:")
print("     int('', 16)          ValueError   -- no digits is not a number")
print("     bytes.fromhex('')    b''          -- no digits is an empty file")

say("6. SO: TWO DOORS, AND THE FIELD DECIDES WHICH ONE")

print("   int(s, 16) / f'{n:x}'         when the field is a QUANTITY")
print("     a length, an offset, a colour, a bitmask, an error code")
print("     -- leading zeros cosmetic, width free, order meaningless")
print()
print("   bytes.fromhex(s) / b.hex()    when the field is DATA")
print("     a hash, a key, a certificate, a packet, an x/xstring from SAP")
print("     -- leading zeros load-bearing, width fixed, order agreed in writing")
print()
field = "0004a1"
print(f"   a three-byte field       {field!r}")
print(f"   as data                  {bytes.fromhex(field).hex(' ')}   {len(bytes.fromhex(field))} bytes, which is what it is")
print(f"   as a quantity            {int(field, 16)}")
print(f"   written back out         {format(int(field, 16), 'x')!r}   the leading zero byte is gone")
try:
    bytes.fromhex(format(int(field, 16), "x"))
except ValueError as exc:
    print(f"   and read as data again   ValueError: {exc}")
print()
print("   That is the whole failure in four lines. Nothing raised until the")
print("   very end, the value was never wrong as a number, and what came")
print("   back is a different length from what went in. Reach for int()")
print("   because a string 'looked like a number' and this is the shape of")
print("   the bug you get -- usually much further downstream than here.")
