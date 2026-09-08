#!/usr/bin/env python3
"""Framing: what a record says about itself, worked on Intel HEX.

Seven sections, each one a claim the page makes:

  1. the record, field by field          -- five fields around the payload
  2. the checksum                         -- four lines, and the sum-to-zero property
  3. one character changed                -- four corruptions, three different refusals
  4. no separator required                -- mark + length is enough to cut the stream
  5. a type the reader has never seen     -- skipped correctly, because of the length
  6. what the frame does not catch        -- two errors that cancel, and a whole record gone
  7. tribit, framed                       -- the same three fields around somebody else's bytes

The layout, the checksum rule and the six record-type numbers are from Intel,
*Hexadecimal Object File Format Specification*, Revision A, January 6, 1988 --
the record mark is a colon, RECLEN is one byte, LOAD OFFSET two, RECTYP one,
INFO/DATA n bytes, CHKSUM one. The checksum is the two's complement of the sum
of the bytes running from RECLEN through the last INFO/DATA byte, so the record
mark is NOT in the sum.
"""

# --------------------------------------------------------------------------
# The frame, in about twenty lines. This is the whole format.
# --------------------------------------------------------------------------

RECORD_TYPES = {
    0x00: "Data",
    0x01: "End of File",
    0x02: "Extended Segment Address",
    0x03: "Start Segment Address",
    0x04: "Extended Linear Address",
    0x05: "Start Linear Address",
}


class Malformed(ValueError):
    """A record the reader refuses before it ever reaches the checksum."""


def checksum(body: bytes) -> int:
    """Two's complement of the sum, over RECLEN .. last DATA byte."""
    return (-sum(body)) & 0xFF


def build(rectyp: int, offset: int, data: bytes) -> str:
    """One record, as the ASCII characters that go in the file."""
    body = bytes([len(data), offset >> 8, offset & 0xFF, rectyp]) + data
    return ":" + (body + bytes([checksum(body)])).hex().upper()


def parse(text: str, at: int) -> tuple[int, int, bytes, bool, int]:
    """Read one record starting at index `at`.

    Returns (rectyp, offset, data, checksum_ok, index just past the record).
    Nothing here looks for a newline: the record mark says where a record
    starts and RECLEN says where it ends. Both of the refusals below happen
    before any checksum is computed -- they are the length doing the checking.
    """
    if text[at:at + 1] != ":":
        raise Malformed(f"no record mark at {at}")
    reclen = int(text[at + 1:at + 3], 16)
    end = at + 1 + (4 + reclen + 1) * 2          # RECLEN..CHKSUM, two chars a byte
    if end > len(text):
        have = (len(text) - at - 1) // 2 - 5
        raise Malformed(f"RECLEN claims {reclen} data bytes, {have} present")
    raw = bytes.fromhex(text[at + 1:end])
    offset = int.from_bytes(raw[1:3], "big")
    return raw[3], offset, raw[4:-1], sum(raw) & 0xFF == 0, end


# --------------------------------------------------------------------------
# 1. THE RECORD, FIELD BY FIELD
# --------------------------------------------------------------------------
print("1. THE RECORD, FIELD BY FIELD")
print()

PAYLOAD = "café".encode("utf-8")          # 63 61 66 c3 a9 -- five bytes, four characters
OFFSET = 0x0100
record = build(0x00, OFFSET, PAYLOAD)

print(f"   payload   {PAYLOAD!r}   {len(PAYLOAD)} bytes: {PAYLOAD.hex(' ')}")
print(f"   record    {record}")
print()
print("   field          chars  value        what it is for")
fields = [
    ("RECORD MARK", record[0:1], "the ASCII colon, 0x3A -- where a record begins"),
    ("RECLEN", record[1:3], f"{len(PAYLOAD)} data bytes follow the type; the maximum is FF"),
    ("LOAD OFFSET", record[3:7], f"0x{OFFSET:04X} -- where the loader puts the first byte"),
    ("RECTYP", record[7:9], "00 = Data; the field that lets one file hold several shapes"),
    ("DATA", record[9:-2], "the payload, one pair of hex digits per byte"),
    ("CHKSUM", record[-2:], "two's complement of RECLEN..DATA"),
]
for name, chars, why in fields:
    print(f"   {name:<13}  {len(chars):>4}  {chars:<11}  {why}")
print()
overhead = len(record) - len(PAYLOAD) * 2
print(f"   {len(PAYLOAD)} bytes of payload arrive as a {len(record)}-character record:")
print(f"   {len(PAYLOAD) * 2} characters of payload in hex, {overhead} characters of frame.")
print(f"   The frame is a constant -- {overhead} characters however long the payload is.")
print()
print(f"   And every character is printable ASCII. The two bytes of the é,")
print(f"   {PAYLOAD[3:].hex(' ')}, are not printable ASCII themselves; they travel as the")
print(f"   four characters {record[15:19]!r}. That is the armour. The frame is the rest.")
print()

# --------------------------------------------------------------------------
# 2. THE CHECKSUM
# --------------------------------------------------------------------------
print("2. THE CHECKSUM IS FOUR LINES")
print()

body = bytes.fromhex(record[1:-2])
running = 0
print("   byte  field         running sum")
labels = ["RECLEN", "LOAD OFFSET", "LOAD OFFSET", "RECTYP"] + ["DATA"] * len(PAYLOAD)
for b, label in zip(body, labels):
    running = (running + b) & 0xFF
    print(f"   {b:02X}    {label:<13} {running:3d}  0x{running:02X}")
print()
print(f"   sum over RECLEN..DATA   {sum(body):5d}  ->  0x{sum(body) & 0xFF:02X} in eight bits")
print(f"   two's complement        {checksum(body):5d}  ->  0x{checksum(body):02X}   <- the CHKSUM field")
print()
whole = body + bytes([checksum(body)])
print("   And the property that makes a reader's job one line: the specification")
print("   says the sum from RECLEN to and including CHKSUM is zero, so a reader")
print("   never has to compute the complement at all -- it adds everything up")
print("   and compares against nothing.")
print(f"   sum(RECLEN..CHKSUM) & 0xFF = {sum(whole) & 0xFF}")
print()
print("   Note what is NOT in the sum: the record mark. A colon corrupted into")
print("   a semicolon is not a checksum failure -- it is a record the reader")
print("   never finds. A frame's own delimiter is the part it cannot check.")
print()

# --------------------------------------------------------------------------
# 3. ONE CHARACTER CHANGED
# --------------------------------------------------------------------------
print("3. ONE CHARACTER CHANGED")
print()

print(f"   good    {record}   checksum ok")
print()
print("   Now change one character. Not a byte of payload -- one ASCII digit,")
print("   which is the damage a text channel actually does.")
print()
print(f"   {'change':<22}{'record':<23}verdict")
for pos, ch, where in ((10, "1", "DATA"), (17, "9", "DATA"), (20, "5", "CHKSUM"), (2, "6", "RECLEN")):
    bad = record[:pos] + ch + record[pos + 1:]
    try:
        rectyp, off, data, ok, _ = parse(bad, 0)
        verdict = "checksum ok" if ok else "checksum FAILED"
    except Malformed as exc:
        verdict = f"Malformed: {exc}"
    label = f"{record[pos]}->{ch} at {pos} in {where}"
    print(f"   {label:<22}{bad}  {verdict}")
print()
print("   Four characters changed, and the last one fails differently. A wrong")
print("   RECLEN never reaches the checksum: the reader is already looking for")
print("   a byte that is not there. A length field is a check too, and it is")
print("   the one that fires first.")
print()
print("   What a failing checksum tells you: this record is wrong. What it does")
print("   not tell you: which character. One 8-bit sum has 256 values and this")
print("   record has 20 characters after the mark, so there is nothing in it")
print("   to locate anything with. Detection, not correction.")
print()

# --------------------------------------------------------------------------
# 4. NO SEPARATOR REQUIRED
# --------------------------------------------------------------------------
print("4. NO SEPARATOR REQUIRED")
print()

FILE = build(0x04, 0x0000, b"\x00\x01") + build(0x00, OFFSET, PAYLOAD) + build(0x01, 0x0000, b"")
print("   Three records, concatenated with nothing at all between them --")
print("   no newline, no space, no length prefix on the file:")
print()
print(f"   {FILE}")
print()
print("   record  type  name                       offset  data")
i = 0
n = 0
while i < len(FILE):
    rectyp, off, data, ok, i = parse(FILE, i)
    n += 1
    name = RECORD_TYPES.get(rectyp, "unknown")
    print(f"   {n:>6}    {rectyp:02X}  {name:<25}  0x{off:04X}  {data.hex(' ') or '(none)'}")
print()
print("   It parses, and that is the length field's real job. The mark says")
print("   where a record starts and RECLEN says where it ends, so the stream")
print("   is self-delimiting: a newline between records is a courtesy to `cat`")
print("   and to `grep`, not something the format needs.")
print()
print("   The alternative -- a delimiter and no length -- is the arrangement")
print("   that breaks the moment the delimiter occurs in data, which is the")
print("   whole subject of in-band signalling. A length field is how a format")
print("   stops caring what its payload contains.")
print()

# --------------------------------------------------------------------------
# 5. A TYPE THE READER HAS NEVER SEEN
# --------------------------------------------------------------------------
print("5. A TYPE THE READER HAS NEVER SEEN")
print()

FUTURE = (
    build(0x00, OFFSET, PAYLOAD)
    + build(0x06, 0x0000, b"\xde\xad\xbe\xef")     # not one of the 1988 six
    + build(0x00, 0x0200, b"\xc5\xbc")             # ż, the Polish letter Latin-1 cannot hold
    + build(0x01, 0x0000, b"")
)
print("   A file written by a newer tool: same three fields, and one record")
print("   whose type this reader has never heard of.")
print()
print(f"   {FUTURE}")
print()
kept, skipped = [], []
i = 0
while i < len(FUTURE):
    rectyp, off, data, ok, i = parse(FUTURE, i)
    if not ok:
        print("   checksum failed -- stop")
        break
    if rectyp in RECORD_TYPES:
        kept.append((rectyp, off, data))
        print(f"   type {rectyp:02X}  {RECORD_TYPES[rectyp]:<24} handled   {data.hex(' ') or '(none)'}")
    else:
        skipped.append((rectyp, data))
        print(f"   type {rectyp:02X}  {'unknown to this reader':<24} SKIPPED   {len(data)} bytes, checksum verified anyway")
print()
recovered = b"".join(d for t, o, d in kept if t == 0x00)
print(f"   recovered payload  {recovered.hex(' ')}  = {recovered.decode('utf-8')!r}")
print(f"   skipped            {len(skipped)} record it could not interpret and did not need to")
print()
print("   This is what a record type is FOR, and it only works because of the")
print("   length. A type alone tells a reader that it does not understand")
print("   something; a type plus a length tells it exactly how far to jump to")
print("   reach the next thing it does. One field is a diagnosis, two are a")
print("   recovery -- and an old reader that survives a new record is the whole")
print("   of what anybody means by an extensible format.")
print()

# --------------------------------------------------------------------------
# 6. WHAT THE FRAME DOES NOT CATCH
# --------------------------------------------------------------------------
print("6. WHAT THE FRAME DOES NOT CATCH")
print()

good = build(0x00, 0x0000, bytes([0x41, 0x42]))
pair = build(0x00, 0x0000, bytes([0x42, 0x41]))
print(f"   two bytes swapped        {good} -> {pair}")
print(f"                            checksum {'still ok' if parse(pair, 0)[3] else 'FAILED'} -- addition does not care about order")
print()
cancel = build(0x00, 0x0000, bytes([0x40, 0x43]))
print(f"   two errors that cancel   {good} -> {cancel}")
print("                            41 42 became 40 43: one down, one up, sum unchanged")
print(f"                            checksum {'still ok' if parse(cancel, 0)[3] else 'FAILED'}")
print()
short = build(0x04, 0x0000, b"\x00\x01") + build(0x01, 0x0000, b"")
print("   a whole record deleted")
print(f"      before  {FILE}")
print(f"      after   {short}")
allok = True
i = 0
while i < len(short):
    *_, ok, i = parse(short, i)
    allok = allok and ok
print(f"      every remaining record's checksum: {'all ok' if allok else 'a failure'}")
print()
print("   Three failures the frame does not see, and they fall into two")
print("   kinds. The first two are inside a record and slip past because an")
print("   8-bit sum is a coarse check: it fails on any single wrong byte and")
print("   on nothing that leaves the total alone. The third is a different")
print("   thing entirely -- the damage is not inside any record, and a")
print("   per-record checksum has no scope to reach it. Nothing about the")
print("   FILE is checked by anything here, and the 1988 specification's six")
print("   record types include no count, no sequence number and no hash.")
print("   Knowing what a check does not cover is the second half of adding one.")
print()

# --------------------------------------------------------------------------
# 7. TRIBIT, FRAMED
# --------------------------------------------------------------------------
print("7. TRIBIT, FRAMED")
print()

TRIBIT_CAFE = bytes.fromhex("543305e1d83740")   # from the tribit page: 'café' packed
print(f"   tribit's own container   {TRIBIT_CAFE.hex(' ')}")
print("      54 33   magic 'T3'    says what the file is")
print("      05      pad count     says how the last byte ends")
print("      e1..    payload       and that is the whole header")
print()
print("   It has a magic number, which Intel HEX does not, and it is missing")
print("   all three of the fields this page is about. Wrap the same bytes:")
print()
framed = build(0x00, 0x0000, TRIBIT_CAFE) + build(0x01, 0x0000, b"")
print(f"   {framed}")
print()
rectyp, off, data, ok, _ = parse(framed, 0)
print(f"   parsed back  type {rectyp:02X}  {len(data)} bytes  checksum {'ok' if ok else 'FAILED'}  {data.hex(' ')}")
print(f"   round trip   {'identical to the tribit bytes' if data == TRIBIT_CAFE else 'DIFFERENT'}")
print()
print(f"   cost  {len(TRIBIT_CAFE)} bytes in, {len(framed)} characters out")
print(f"         {len(TRIBIT_CAFE) * 2} are the payload in hex")
print(f"         {overhead} are this record's frame")
eof = build(0x01, 0x0000, b"")
print(f"         {len(eof)} are the end-of-file record, {eof}, which is those")
print("         same characters in every Intel HEX file ever written")
print()
print("   That is the trade, and it is worth writing down before choosing it:")
print(f"   2x for the armour, a fixed {overhead} characters per record for the frame.")
print("   In exchange, a file that survives a 7-bit channel, that cuts into")
print("   records without a delimiter, that a reader can skip through when it")
print("   meets something new, and that says NO when it has been damaged")
print("   instead of quietly handing back the wrong bytes.")
