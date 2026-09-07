"""The table utf8(5) prints, rebuilt from arithmetic, beside the one in force.

The man page on a 2026 Mac is dated 2004 and cites RFC 2279 (1998).  RFC 3629
replaced it in 2003.  Neither table is looked up here: both are generated from
the byte templates, so this program says the same thing on any machine, and
what it prints can be held against the page on yours.
"""

def payload_bits(n: int) -> int:
    """Free bits in an n-byte UTF-8 sequence: 8-n-1 in the lead, 6 per tail."""
    return 7 if n == 1 else (7 - n) + 6 * (n - 1)


def template(n: int) -> str:
    if n == 1:
        return "0bbbbbbb"
    lead = "1" * n + "0" + "b" * (7 - n)
    return ", ".join([lead] + ["10bbbbbb"] * (n - 1))


RFC3629_MAX = 0x10FFFF          # 2003: capped to what UTF-16 can name
RFC2279_MAX = 0x7FFFFFFF        # 1998: 31 bits, up to six bytes

print("1. THE TABLE utf8(5) PRINTS -- RFC 2279, 1 TO 6 BYTES")
print("   n  bits  highest       template")
lo = 0
for n in range(1, 7):
    hi = (1 << payload_bits(n)) - 1
    print(f"   {n}  {payload_bits(n):>4}  0x{hi:08X}    {template(n)}")
    lo = hi + 1
print(f"   The last row reaches 0x{RFC2279_MAX:08X}: 31 bits, six bytes.")
print()

print("2. THE TABLE IN FORCE -- RFC 3629, 2003, 1 TO 4 BYTES")
print("   n  bits  highest       still reachable")
for n in range(1, 7):
    hi = (1 << payload_bits(n)) - 1
    reach = min(hi, RFC3629_MAX)
    if hi <= RFC3629_MAX:
        note = f"0x{reach:08X}"
    elif reach > ((1 << payload_bits(n - 1)) - 1):
        note = f"0x{reach:08X}  (row truncated)"
    else:
        note = "-             (row deleted)"
    print(f"   {n}  {payload_bits(n):>4}  0x{hi:08X}    {note}")
print()

print("3. WHAT THE 2003 CAP ACTUALLY REMOVED")
removed = RFC2279_MAX - RFC3629_MAX
print(f"   highest code point, 1998 rule   0x{RFC2279_MAX:08X}  = {RFC2279_MAX:>10,}")
print(f"   highest code point, 2003 rule   0x{RFC3629_MAX:08X}  = {RFC3629_MAX:>10,}")
print(f"   numbers no longer encodable                 {removed:>10,}")
print(f"   that is {removed / (RFC2279_MAX + 1):.1%} of the old space, and the")
print("   whole of the 5- and 6-byte forms.  A decoder written from the older")
print("   table accepts every one of them, which is why 'valid UTF-8' is not")
print("   one question -- see 03_Encodings/validation_is_a_boundary.")
print()

print("4. THE ARITHMETIC, CHECKED AGAINST PYTHON'S OWN CODEC")


def encode_3629(cp: int) -> bytes:
    for n in range(1, 5):
        if cp < (1 << payload_bits(n)) and cp <= RFC3629_MAX:
            if n == 1:
                return bytes([cp])
            lead = (0xFF << (8 - n)) & 0xFF
            out = [lead | (cp >> (6 * (n - 1)))]
            out += [0x80 | ((cp >> (6 * k)) & 0x3F) for k in range(n - 2, -1, -1)]
            return bytes(out)
    raise ValueError(f"U+{cp:04X} is not encodable under RFC 3629")


sample = [0x41, 0xE9, 0x17C, 0x20AC, 0x1F600, 0x10FFFF]
for cp in sample:
    mine = encode_3629(cp)
    theirs = chr(cp).encode("utf-8")
    print(f"   U+{cp:06X}  {mine.hex(' '):<12} {'==' if mine == theirs else '!='} codec")
assert all(encode_3629(cp) == chr(cp).encode("utf-8") for cp in sample)
for cp in (0x110000, 0x200000):
    try:
        encode_3629(cp)
    except ValueError as exc:
        print(f"   U+{cp:06X}  {exc}")
print()
print("   Six agreements and two refusals.  The refusals are the rows the")
print("   1998 table has and the 2004 man page still prints.")
