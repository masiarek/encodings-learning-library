"""Answer key: the same character, spelled twice, and why the longer one is banned.

The kata's hard question is not what happens -- Python refuses -- but WHY a
spelling that carries identical payload bits and would decode to the identical
character is ill-formed rather than merely unusual.
"""
LEGAL = b"\x2f"                 # '/'  -- one byte, the only legal spelling
OVERLONG = b"\xc0\xaf"          # the same code point, padded into two bytes

def payload(bs: bytes) -> str:
    if len(bs) == 1:
        return f"{bs[0]:08b}"
    return f"{bs[0] & 0x1F:05b} {bs[1] & 0x3F:06b}"

print(f"legal     {LEGAL.hex(' '):<8} bits {payload(LEGAL)}")
print(f"overlong  {OVERLONG.hex(' '):<8} bits {payload(OVERLONG)}")
print(f"the payload of both, as a number: {LEGAL[0]} and "
      f"{((OVERLONG[0] & 0x1F) << 6) | (OVERLONG[1] & 0x3F)}")
print("Same value. A decoder that just assembles the bits gets '/' from both.")
print()
try:
    OVERLONG.decode("utf-8")
    print("decoded -- which would be news")
except UnicodeDecodeError:
    print("Python: UnicodeDecodeError -- refused, and it is right to")
print()
print("WHY REFUSING IS NOT PEDANTRY")
print()
print("The moment one character has two byte strings, a check that reads BYTES")
print("and a step that reads CHARACTERS can be made to disagree -- and they")
print("will disagree in the attacker's favour, because the check runs first.")
print()
print("   a filter looks for the byte 2f              -- the path separator")
print("   the request carries c0 af                   -- not 2f, filter passes")
print("   a lenient decoder later yields '/'          -- and the path escapes")
print()
print("That is not hypothetical: it is the shape of the IIS directory-traversal")
print("bug, and it is why RFC 3629 made the shortest form a REQUIREMENT rather")
print("than a recommendation. One character, one spelling, so the two readings")
print("cannot come apart.")
print()
print("THE RULE, AS ARITHMETIC")
for cp, n in [(0x2F, 1), (0x80, 2), (0x800, 3), (0x10000, 4)]:
    print(f"   U+{cp:04X} first needs {n} byte(s); anything longer for this "
          f"code point is overlong")
print("   So each length has a minimum code point, and a sequence is legal only")
print("   if its value reaches its own length's floor. Two bytes must carry at")
print("   least U+0080; c0 and c1 can never begin a legal sequence at all,")
print("   which is why they appear nowhere in valid UTF-8.")
print()
print("AND THE SAME TRAP WITHOUT THE ENCODING")
print("   canonicalize, THEN check. Any time a value has more than one")
print("   representation -- overlong UTF-8, %2f in a URL, a Windows short")
print("   filename, a trailing dot -- a check that runs before normalization is")
print("   checking a different string from the one that gets used.")

assert ((OVERLONG[0] & 0x1F) << 6) | (OVERLONG[1] & 0x3F) == 0x2F
# c0 and c1 can never start a legal sequence: proved, not asserted from memory.
_starts = {chr(c).encode()[0] for c in range(0x110000) if not 0xD800 <= c < 0xE000}
assert 0xC0 not in _starts and 0xC1 not in _starts
