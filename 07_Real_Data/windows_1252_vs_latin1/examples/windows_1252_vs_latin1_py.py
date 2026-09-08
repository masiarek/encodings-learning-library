"""Windows-1252 against ISO-8859-1, byte by byte.

The question the whole file answers: is cp1252 a SUPERSET of Latin-1?
A superset would keep every mapping Latin-1 makes and add more on top.
Section 2 counts what cp1252 actually does to those mappings.
"""

LATIN1 = "latin-1"
CP1252 = "cp1252"


def decode_or_none(byte_value, table):
    """Return the character, or None if the table has no entry for this byte."""
    try:
        return bytes([byte_value]).decode(table)
    except UnicodeDecodeError:
        return None


def show(ch):
    """A printable spelling for a character that may be a control or absent."""
    if ch is None:
        return "--"
    if ch.isprintable():
        return f" {ch}"
    return f"U+{ord(ch):04X}"


print("1. WHERE THE TWO TABLES STAND ON EVERY BYTE")
print("-" * 72)
agree, remapped, unassigned = [], [], []
for b in range(256):
    left = decode_or_none(b, LATIN1)
    right = decode_or_none(b, CP1252)
    if right is None:
        unassigned.append(b)
    elif left == right:
        agree.append(b)
    else:
        remapped.append(b)

print(f"   identical in both tables        {len(agree):3} bytes")
print(f"   cp1252 maps to a DIFFERENT char {len(remapped):3} bytes")
print(f"   cp1252 has NO entry at all      {len(unassigned):3} bytes")
print(f"   {'':31} {len(agree) + len(remapped) + len(unassigned):3} total")
lo, hi = min(remapped + unassigned), max(remapped + unassigned)
print()
print(f"   Every byte in the last two rows lies in 0x{lo:02X}-0x{hi:02X}, and that")
print("   range is 32 bytes wide -- so the two tables agree everywhere else.")
print()

print("2. SO IS CP1252 A SUPERSET OF LATIN-1?")
print("-" * 72)
print("   A superset would keep every mapping and add more. Count the bytes")
print("   where cp1252 KEEPS what Latin-1 says, over the disputed 32:")
kept = [b for b in range(0x80, 0xA0) if decode_or_none(b, CP1252) == decode_or_none(b, LATIN1)]
print(f"      kept: {len(kept)} of 32")
print("   Zero. Every one of the 32 is either given away to another")
print("   character or dropped, so cp1252 REPLACES that block rather than")
print("   extending it. There is no byte on which cp1252 says everything")
print("   Latin-1 says and more -- which is what 'superset' would require.")
print()

print("3. THE DISPUTED BLOCK, SIDE BY SIDE")
print("-" * 72)
print("   byte   ISO-8859-1        Windows-1252")
for b in range(0x80, 0xA0):
    left = decode_or_none(b, LATIN1)
    right = decode_or_none(b, CP1252)
    note = "   <- no entry in cp1252" if right is None else ""
    print(f"   0x{b:02X}   {show(left):<10}{show(right)}{note}".rstrip())
print()
print("   The left column is the C1 control range, U+0080 to U+009F.")
print("   ISO-8859-1 assigns no printable character there at all; the control")
print("   functions that use the range are defined by ISO/IEC 6429, and almost")
print("   nothing emits them. That is why the block was available to take.")
print()

print("4. THE FIVE BYTES CP1252 LEAVES EMPTY")
print("-" * 72)
print("   " + " ".join(f"0x{b:02X}" for b in unassigned))
print()
print("   Latin-1 maps all 256 byte values, so decoding under it CANNOT fail.")
print("   cp1252 maps 251. Those five are the difference between a table that")
print("   always round-trips and one that does not, which is the subject of")
print("   the mojibake round-trip page.")
for table in (LATIN1, CP1252):
    ok = sum(1 for b in range(256) if decode_or_none(b, table) is not None)
    print(f"      {table:8} decodes {ok:3} of 256 single bytes")
print()

print("5. THE EURO IS THE SHARPEST SINGLE CASE")
print("-" * 72)
print(f"   '\N{EURO SIGN}' in cp1252     -> {'€'.encode(CP1252).hex()}")
try:
    "€".encode(LATIN1)
    print("   unexpectedly encoded under Latin-1")
except UnicodeEncodeError as exc:
    print(f"   '\N{EURO SIGN}' in Latin-1    -> {type(exc).__name__}: {exc.reason}")
print()
print("   ISO-8859-1 dates from 1987 and the euro sign postdates it by about a")
print("   decade, so the character is simply not in that table. This is why an")
print("   interface declared as Latin-1 can never carry a euro sign, whatever")
print("   the sender does -- ISO-8859-15 was published to add it, at 0xA4.")
print()

print("6. WHICH TABLE WAS WRONGLY APPLIED? NOT EVERY CHARACTER TELLS YOU")
print("-" * 72)
print("   Take UTF-8 bytes and read them under each of the two tables.")
print()
for original in ("\N{LATIN SMALL LETTER E WITH ACUTE}", "\N{EURO SIGN}"):
    raw = original.encode("utf-8")
    row = []
    for table in (LATIN1, CP1252):
        try:
            row.append(ascii(raw.decode(table)))
        except UnicodeDecodeError:
            row.append("<decode failed>")
    verdict = "IDENTICAL -- tells you nothing" if row[0] == row[1] else "DIFFERENT -- names the table"
    print(f"   {original!r} = {raw.hex(' ')}")
    print(f"      as Latin-1 : {row[0]}")
    print(f"      as cp1252  : {row[1]}")
    print(f"      {verdict}")
    print()
print("   The reason is in section 1: the two tables differ only on 0x80-0x9F.")
print("   The bytes of 'e-acute' are 0xC3 0xA9, both outside that block, so")
print("   both tables give the same garbage. The euro's UTF-8 bytes include")
print("   0x82, which IS inside it -- so the middle character differs, and")
print("   that one character names the table the reader used.")
print()

print("7. WHAT THE WEB DECIDED")
print("-" * 72)
print("   The WHATWG Encoding Standard lists 17 labels for windows-1252, and")
print("   'iso-8859-1', 'latin1', 'ascii' and 'us-ascii' are four of them --")
print("   so a browser told a page is Latin-1 reads it as cp1252 on purpose,")
print("   and so does one told the page is ASCII.")
print()
print("   That is a decision about labels on the web. It is NOT a licence to")
print("   treat the two as interchangeable in a file interface, where the")
print("   five unassigned bytes decide whether a repair is possible at all.")
print("   Label list checked against https://encoding.spec.whatwg.org/,")
print("   2026-09-07.")
