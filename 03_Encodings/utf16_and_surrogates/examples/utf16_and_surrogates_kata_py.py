"""Answer key: one emoji, three length answers, and the 2,048 holes it explains.

The kata asks for the surrogate pair by hand and then for three consequences
that all come from the same arithmetic.
"""
CP = 0x1F600

v = CP - 0x10000
hi, lo = 0xD800 + (v >> 10), 0xDC00 + (v & 0x3FF)
print(f"U+{CP:04X}  minus 0x10000 = {v:#07x} = {v:020b}  (20 bits)")
print(f"   high ten bits {v >> 10:010b} + D800 -> U+{hi:04X}")
print(f"   low  ten bits {v & 0x3FF:010b} + DC00 -> U+{lo:04X}")
print(f"   utf-16-be     {chr(CP).encode('utf-16-be').hex(' ')}  -- and there is the pair")
print()
print("THREE LENGTHS FOR ONE CHARACTER")
s = chr(CP)
print(f"   Python len()            {len(s)}   Python counts CODE POINTS")
print(f"   UTF-16 code units       {len(s.encode('utf-16-le')) // 2}   what Java, JavaScript, C# and SAP count")
print(f"   UTF-8 bytes             {len(s.encode('utf-8'))}   what a database column is measured in")
print("   None of the three is wrong. They answer different questions, and a")
print("   VARCHAR(1) that rejects this character is counting one of them.")
print()
print("THE 2,048 CODE POINTS THAT CAN NEVER BE CHARACTERS")
print(f"   high surrogates U+D800..U+DBFF  {0xDBFF - 0xD800 + 1} of them")
print(f"   low  surrogates U+DC00..U+DFFF  {0xDFFF - 0xDC00 + 1} of them")
print(f"   total {0xDFFF - 0xD800 + 1}")
print("   They are reserved so that a UTF-16 reader can tell a lone unit from")
print("   half a pair, which means Unicode had to spend a block of its own")
print("   number space on a property of ONE encoding. They are permanently")
print("   unassigned, and a string containing one is not encodable in UTF-8.")
try:
    chr(0xD800).encode("utf-8")
    print("   encoded -- which would be news")
except UnicodeEncodeError:
    print("   chr(0xD800).encode('utf-8') -> UnicodeEncodeError, exactly so")
print()
print("AND WHY UNICODE STOPS AT U+10FFFF")
print(f"   the pair carries 10 + 10 = 20 bits, plus the 0x10000 offset")
print(f"   0x10000 + 2**20 - 1 = {0x10000 + 2**20 - 1:#X}")
print("   That is not a round number and it is not a design goal: it is the")
print("   largest value UTF-16 can express. The ceiling of the whole character")
print("   set is a fact about a 1996 encoding, kept ever since so that the")
print("   three UTF forms can encode exactly the same set.")

assert chr(CP).encode("utf-16-be") == bytes([hi >> 8, hi & 0xFF, lo >> 8, lo & 0xFF])
assert 0x10000 + 2**20 - 1 == 0x10FFFF
