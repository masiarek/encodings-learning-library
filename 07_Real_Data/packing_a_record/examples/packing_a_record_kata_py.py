"""Answer key: six questions about one fourteen-byte record.

Five of them have the same answer on every machine, which is what makes them
answerable at all. The sixth does not, and noticing that is the question.

Run:  python3 packing_a_record_kata_py.py
"""

import struct

RULE = "-" * 72
NAME = "Zażółć"
RAW = NAME.encode("utf-8")


def head(n, title):
    print(f"\n{n}. {title}\n{RULE}\n")


def cls(e):
    mod = type(e).__module__
    return type(e).__name__ if mod == "builtins" else f"{mod}.{type(e).__name__}"


# ------------------------------------------------------------------ 1
head(1, "HOW LONG IS THE RECORD?")

for fmt in (">Ih10s", "<Ihd", "<Ihxxd"):
    print(f"   {f"struct.calcsize('{fmt}')":<28} {struct.calcsize(fmt):>2}")
print()
print("   4 + 2 + 10, 4 + 2 + 8, and the same again with two 'x' pads you")
print("   asked for by name. In standard mode a format string's length is")
print("   arithmetic you can do on paper -- which is the property the")
print("   unprefixed spelling gives away.")

# ------------------------------------------------------------------ 2
head(2, "THE SAME NUMBER, THE TWO ORDERS")

print(f"   struct.pack('>I', 4711).hex()   {struct.pack('>I', 4711).hex()}")
print(f"   struct.pack('<I', 4711).hex()   {struct.pack('<I', 4711).hex()}")
print()
print("   Big-endian puts the most significant byte first, so 4711 -- which")
print("   is 0x1267 -- reads straight off as 00 00 12 67. Little-endian is")
print("   the same four bytes backwards. Two leading zeros either way,")
print("   because the field is four bytes wide and the number is not.")

# ------------------------------------------------------------------ 3
head(3, "AND WHAT THE WRONG READER MAKES OF IT")

be = struct.pack(">I", 4711)
print(f"   struct.unpack('>I', be)[0]   {struct.unpack('>I', be)[0]:>12}")
print(f"   struct.unpack('<I', be)[0]   {struct.unpack('<I', be)[0]:>12}")
print()
print("   Both are valid unsigned 32-bit integers, so the wrong one raises")
print("   nothing, logs nothing, and looks like an ordinary large id. If you")
print("   predicted 'an error' here, that is the habit this page is aimed at.")

# ------------------------------------------------------------------ 4
head(4, "WHICH OF THE TWO PACKS RAISES, AND WITH WHAT CLASS")

try:
    struct.pack("<10s", NAME)
except Exception as e:
    print(f"   struct.pack('<10s', 'Zażółć')            {cls(e)}")
print(f"   struct.pack('<10s', 'Zażółć'.encode())   {struct.pack('<10s', RAW).hex(' ')}")
print()
print("   's' packs bytes and will not encode a str for you. The class is")
print("   struct.error and NOT TypeError, so `except TypeError` around a pack")
print("   catches nothing -- which is the half of this answer most people")
print("   miss even after predicting the raise correctly.")

# ------------------------------------------------------------------ 5
head(5, "TEN BYTES OF NAME INTO A NINE-BYTE FIELD")

nine = struct.pack("<9s", RAW)
print(f"   len('Zażółć')            {len(NAME):>2} characters")
print(f"   len(encoded)             {len(RAW):>2} bytes")
print(f"   struct.pack('<9s', ...)  {nine.hex(' ')}")
print()
try:
    nine.decode("utf-8")
except UnicodeDecodeError as e:
    print(f"   nine.decode('utf-8')     {cls(e)}")
print(f"   with errors='replace'    {nine.decode('utf-8', 'replace')!r}")
print()
print("   No exception from the pack: 's' truncates on the right in silence.")
print("   The exception arrives later and somewhere else, in whatever tries")
print("   to read the file -- which is why the check belongs before the pack,")
print("   not after it.")

# ------------------------------------------------------------------ 6
head(6, "AND THE ONE YOU COULD NOT HAVE ANSWERED")

std = struct.calcsize("<Ihd")
print("   struct.calcsize('Ihd')  =  ?")
print()
print("   There is no right answer to write down. With no prefix the format")
print("   is NATIVE: the widths and the alignment padding come from the C")
print("   compiler that built this Python, so the number is a property of the")
print("   machine you ran it on and not of the string 'Ihd'.")
print()
print("   What can be checked is the shape, and it is the finding:")
print(f"     struct.calcsize('Ihd') == struct.calcsize('<Ihd')   "
      f"{struct.calcsize('Ihd') == std}")
print()
print("   If you answered 14 -- the sum of the field widths -- you made")
print("   exactly the assumption the unprefixed format invites, and the")
print("   record you write will be a different length on somebody else's")
print("   machine. Naming the order (`<`, `>` or `!`) fixes the widths and")
print("   removes the padding in the same character.")
print()
